"""Behavioral checks for the finite-pool rank audit, using only unittest."""

import itertools
import math
import unittest


from goodhart_audit.core import (
    envelope_proposal,
    estimate_risk,
    full_envelope,
    partial_bounds,
    rank_weights,
)


class RankWeightTests(unittest.TestCase):
    def test_winner_weights_match_enumeration_of_every_subset(self):
        # A uniform n-subset wins at its smallest (best) zero-based rank.
        for m in range(1, 10):
            for n in range(1, m + 1):
                counts = [0] * m
                subsets = list(itertools.combinations(range(m), n))
                for subset in subsets:
                    counts[min(subset)] += 1
                actual = rank_weights(m, n)
                with self.subTest(m=m, n=n):
                    self.assertEqual(len(actual), m)
                    for count, weight in zip(counts, actual):
                        self.assertAlmostEqual(weight, count / len(subsets), places=14)
                    self.assertAlmostEqual(math.fsum(actual), 1.0, places=14)

    def test_rank_endpoints_use_descending_order(self):
        self.assertEqual(rank_weights(4, 1), [0.25, 0.25, 0.25, 0.25])
        self.assertEqual(rank_weights(4, 4), [1.0, 0.0, 0.0, 0.0])
        self.assertEqual(rank_weights(1, 1), [1.0])

    def test_large_pool_law_remains_normalized_despite_recurrence_roundoff(self):
        weights = rank_weights(1_000_000, 2)
        self.assertAlmostEqual(math.fsum(weights), 1.0, places=14)

    def test_risk_need_not_increase_with_search_budget(self):
        # The second-best candidate is bad; the best is safe.
        risks = [rank_weights(4, n)[1] for n in range(1, 5)]
        self.assertAlmostEqual(risks[0], 0.25)
        self.assertAlmostEqual(risks[1], 1 / 3)
        self.assertEqual(risks[-1], 0.0)
        self.assertGreater(risks[1], risks[0])

    def test_invalid_pool_sizes_and_budgets_fail(self):
        for m, n in [(0, 1), (-1, 1), (4, 0), (4, 5), (4.0, 2),
                     (4, 2.0), (True, 1), (4, False), (4, math.inf)]:
            with self.subTest(m=m, n=n), self.assertRaises(ValueError):
                rank_weights(m, n)


class EnvelopeTests(unittest.TestCase):
    @staticmethod
    def enumerated_weights(m, n):
        counts = [0] * m
        count = 0
        for subset in itertools.combinations(range(m), n):
            counts[min(subset)] += 1
            count += 1
        return [value / count for value in counts]

    def test_grid_envelope_has_constant_maximum_importance_ratio(self):
        # Hand-computed envelope for m=3, budgets 1 and 3.
        q, z = envelope_proposal(3, [1, 3])
        self.assertAlmostEqual(z, 5 / 3)
        for actual, expected in zip(q, [3 / 5, 1 / 5, 1 / 5]):
            self.assertAlmostEqual(actual, expected)
        for r in range(3):
            maximum = max(self.enumerated_weights(3, n)[r] for n in [1, 3])
            self.assertAlmostEqual(maximum / q[r], z)

    def test_full_envelope_matches_exhaustive_small_pool_search(self):
        for m in range(1, 12):
            for cap in range(1, m + 1):
                maxima = [max(self.enumerated_weights(m, n)[r]
                              for n in range(1, cap + 1)) for r in range(m)]
                expected_z = math.fsum(maxima)
                q, z = full_envelope(m, cap)
                with self.subTest(m=m, cap=cap):
                    self.assertAlmostEqual(z, expected_z, places=13)
                    for actual, maximum in zip(q, maxima):
                        self.assertAlmostEqual(actual, maximum / expected_z, places=13)

    def test_full_envelope_agrees_with_grid_on_larger_pool(self):
        for m, cap in [(80, 40), (257, 257), (1000, 17)]:
            q, z = full_envelope(m, cap)
            grid_q, grid_z = envelope_proposal(m, list(range(1, cap + 1)))
            self.assertAlmostEqual(z, grid_z, places=12)
            for value, grid_value in zip(q, grid_q):
                self.assertAlmostEqual(value, grid_value, places=13)

    def test_harmonic_sandwich_and_adjacent_total_variation_identity(self):
        for m in range(1, 25):
            q, z = full_envelope(m)
            harmonic = math.fsum(1 / r for r in range(1, m + 1))
            self.assertGreaterEqual(z + 1e-12, harmonic / math.e)
            self.assertLessEqual(z, harmonic + 1e-12)
            laws = [rank_weights(m, n) for n in range(1, m + 1)]
            total_variation = math.fsum(
                math.fsum(abs(x - y) for x, y in zip(a, b)) / 2
                for a, b in zip(laws, laws[1:])
            )
            self.assertAlmostEqual(z, 1 + total_variation, places=12)
            self.assertAlmostEqual(math.fsum(q), 1.0, places=13)

    def test_grid_without_budget_one_may_have_unused_zero_mass(self):
        self.assertEqual(envelope_proposal(3, [3]), ([1.0, 0.0, 0.0], 1.0))

    def test_envelope_rejects_underflow_that_would_remove_target_support(self):
        with self.assertRaisesRegex(ValueError, "underflow"):
            envelope_proposal(2048, [1024])

    def test_empty_duplicate_and_invalid_budget_grids_fail(self):
        for budgets in [[], [1, 1], [0], [4], [True], [1.5]]:
            with self.subTest(budgets=budgets), self.assertRaises(ValueError):
                envelope_proposal(3, budgets)
        for cap in [0, 4, True, 1.5, math.nan]:
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                full_envelope(3, cap)


class EstimateTests(unittest.TestCase):
    def test_importance_mean_is_unbiased_for_every_binary_label_vector(self):
        # Average the estimator over every IID two-draw sequence.
        proposal = [0.5, 0.3, 0.2]
        for labels in itertools.product([0.0, 1.0], repeat=3):
            expectation = [0.0, 0.0, 0.0]
            for pair in itertools.product(range(3), repeat=2):
                probability = proposal[pair[0]] * proposal[pair[1]]
                rows = estimate_risk(pair, [labels[r] for r in pair], proposal, [1, 2, 3])
                for index, row in enumerate(rows):
                    expectation[index] += probability * row["estimate"]
            truths = [sum(labels) / 3, (2 * labels[0] + labels[1]) / 3, labels[0]]
            for actual, expected in zip(expectation, truths):
                self.assertAlmostEqual(actual, expected, places=13)

    def test_empirical_bernstein_uses_sample_variance_and_two_sided_union_factor(self):
        rows = estimate_risk([0, 1, 0, 1], [1, 0, 1, 0], [0.5, 0.5], [1, 2], 0.1)
        log_factor = math.log(80)
        # Budget 1 observations [1, 0, 1, 0], unbiased sample variance 1/3.
        expected = math.sqrt(2 * (1 / 3) * log_factor / 4) + 7 * log_factor / 9
        self.assertAlmostEqual(rows[0]["estimate"], 0.5)
        self.assertAlmostEqual(rows[0]["radius"], expected)
        self.assertAlmostEqual(rows[0]["max_weight"], 1.0)
        self.assertAlmostEqual(rows[1]["max_weight"], 2.0)

    def test_raw_estimate_can_exceed_one_without_biasing_by_clipping(self):
        row = estimate_risk([0, 0], [1, 1], [0.1, 0.9], [2])[0]
        self.assertEqual(row["estimate"], 10.0)
        self.assertEqual((row["lower"], row["upper"]), (0.0, 1.0))

    def test_zero_observed_failures_retain_positive_uncertainty(self):
        row = estimate_risk([0] * 1000, [0] * 1000, [1.0], [1])[0]
        self.assertEqual(row["estimate"], 0.0)
        self.assertEqual(row["lower"], 0.0)
        self.assertGreater(row["upper"], 0.0)
        self.assertLess(row["upper"], 1.0)

    def test_constant_fractional_loss_has_finite_interval(self):
        row = estimate_risk([0] * 1000, [0.25] * 1000, [1.0], [1])[0]
        self.assertEqual(row["estimate"], 0.25)
        self.assertLess(row["lower"], 0.25)
        self.assertGreater(row["upper"], 0.25)
        self.assertTrue(math.isfinite(row["radius"]))

    def test_mean_does_not_underflow_when_global_bound_dwarfs_observations(self):
        row = estimate_risk([1] * 1000, [1e-16] * 1000, [1e-308, 1.0], [1])[0]
        self.assertGreater(row["estimate"], 0.0)
        self.assertAlmostEqual(row["estimate"] / 5e-17, 1.0, places=13)
        self.assertTrue(math.isfinite(row["radius"]))

    def test_subnormal_observations_survive_mean_calculation(self):
        tiny = math.ulp(0.0)
        row = estimate_risk([0, 0], [tiny, tiny], [1.0], [1])[0]
        self.assertEqual(row["estimate"], tiny)

    def test_budget_order_is_preserved(self):
        rows = estimate_risk([0, 1], [0, 1], [0.5, 0.5], [2, 1])
        self.assertEqual([row["budget"] for row in rows], [2, 1])

    def test_zero_mass_outside_all_target_support_is_allowed(self):
        row = estimate_risk([0, 0], [0.5, 0.5], [1.0, 0.0], [2])[0]
        self.assertEqual(row["estimate"], 0.5)

    def test_target_support_is_checked_even_if_missing_rank_was_not_drawn(self):
        with self.assertRaises(ValueError):
            estimate_risk([0, 0], [0, 0], [1.0, 0.0], [1])

    def test_invalid_draws_losses_probabilities_and_confidence_fail(self):
        invalid = [
            ([], [], [0.5, 0.5], [1], 0.05),
            ([0], [0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [0], [0.5, 0.5], [1], 0.05),
            ([0, 2], [0, 1], [0.5, 0.5], [1], 0.05),
            ([0, -1], [0, 1], [0.5, 0.5], [1], 0.05),
            ([True, 0], [0, 1], [0.5, 0.5], [1], 0.05),
            ([0.0, 0], [0, 1], [0.5, 0.5], [1], 0.05),
            ([0, 1], [math.nan, 0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [math.inf, 0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [-0.1, 0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [1.1, 0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [False, 0], [0.5, 0.5], [1], 0.05),
            ([0, 1], [0, 0], [0.2, 0.2], [1], 0.05),
            ([0, 1], [0, 0], [-0.1, 1.1], [1], 0.05),
            ([0, 1], [0, 0], [math.nan, 1], [1], 0.05),
            ([0, 1], [0, 0], [True, 0], [1], 0.05),
            ([0, 1], [0, 0], [], [1], 0.05),
            ([0, 1], [0, 0], [0.5, 0.5], [], 0.05),
            ([0, 1], [0, 0], [0.5, 0.5], [1, 1], 0.05),
            ([0, 0], [0, 0], [0.0, 1.0], [2], 0.05),
        ]
        invalid.extend(([0, 1], [0, 0], [0.5, 0.5], [1], delta)
                       for delta in [0, 1, -0.1, math.nan, math.inf, True])
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError):
                estimate_risk(*args)


class PartialIdentificationTests(unittest.TestCase):
    def test_partial_interval_matches_all_completions_of_missing_labels(self):
        labels = [0.25, None, 1.0, None]
        weights = [0.1, 0.2, 0.3, 0.4]
        lower, upper = partial_bounds(labels, weights)
        completions = [0.025 + 0.2 * a + 0.3 + 0.4 * b
                       for a, b in itertools.product([0, 1], repeat=2)]
        self.assertAlmostEqual(lower, min(completions))
        self.assertAlmostEqual(upper, max(completions))

    def test_all_missing_and_fully_known_bounds(self):
        self.assertEqual(partial_bounds([None, None], [0.4, 0.6]), (0.0, 1.0))
        self.assertEqual(partial_bounds([0.25, 0.75], [0.5, 0.5]), (0.5, 0.5))
        self.assertEqual(partial_bounds([0.25, None], [1.0, 0.0]), (0.25, 0.25))

    def test_invalid_labels_weights_and_lengths_fail(self):
        for labels, weights in [([], []), ([0], [0.5, 0.5]),
                                ([None, None], [0.2, 0.2]),
                                ([math.nan], [1]), ([math.inf], [1]),
                                ([-0.1], [1]), ([1.1], [1]),
                                ([True], [1]), ([0], [-1]), ([0], [math.nan])]:
            with self.subTest(labels=labels, weights=weights), self.assertRaises(ValueError):
                partial_bounds(labels, weights)


if __name__ == "__main__":
    unittest.main()
