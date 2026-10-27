"""Exact small-population checks for the weighted-WoR betting engine."""

import itertools
import math
import unittest

from goodhart_audit.anytime import DEFAULT_BETS, FinitePoolAudit, weighted_order


def order_probability(order, proposal):
    """Probability of a permutation under proportional remaining-weight draws."""
    remaining = set(order)
    probability = 1.0
    for index in order:
        probability *= proposal[index] / math.fsum(proposal[j] for j in remaining)
        remaining.remove(index)
    return probability


class AnytimeWealthTests(unittest.TestCase):
    def test_zero_queries_return_full_interval_and_unit_wealth(self):
        audit = FinitePoolAudit([[0.2, 0.8]], [0.5, 0.5])
        row = audit.bounds()[0]
        self.assertEqual((row["lower"], row["upper"]), (0.0, 1.0))
        self.assertEqual(row["label_count"], 0)
        self.assertFalse(row["interval_conflict"])
        self.assertEqual(audit.log_wealth(0, 0.3, "upper"), 0.0)

    def test_mixture_wealth_has_mean_one_at_every_time_for_all_binary_labels(self):
        proposal = [0.5, 0.3, 0.2]
        targets = [[0.5, 0.25, 0.25], [0.0, 0.4, 0.6]]
        for labels in itertools.product([0, 1], repeat=3):
            truths = [math.fsum(a * y for a, y in zip(target, labels)) for target in targets]
            expected = {(t, k, direction): 0.0 for t in range(1, 4)
                        for k in range(2) for direction in ["upper", "lower"]}
            for order in itertools.permutations(range(3)):
                probability = order_probability(order, proposal)
                audit = FinitePoolAudit(targets, proposal)
                for t, index in enumerate(order, 1):
                    audit.observe(index, labels[index])
                    for k, truth in enumerate(truths):
                        for direction in ["upper", "lower"]:
                            expected[t, k, direction] += probability * math.exp(
                                audit.log_wealth(k, truth, direction))
            for key, value in expected.items():
                with self.subTest(labels=labels, key=key):
                    self.assertAlmostEqual(value, 1.0, places=11)

    def test_fractional_observation_matches_hand_calculated_mixture(self):
        audit = FinitePoolAudit([[0.25, 0.75]], [0.5, 0.5], bets=(1.0, 0.5))
        audit.observe(0, 0.6)
        # D=1.5, c=1.5, Y=0.2, m(0.45)=0.3.
        upper = ((0.8 / 0.7) + (0.5 + 0.5 * 0.8 / 0.7)) / 2
        lower = ((0.2 / 0.3) + (0.5 + 0.5 * 0.2 / 0.3)) / 2
        self.assertAlmostEqual(math.exp(audit.log_wealth(0, 0.45, "upper")), upper)
        self.assertAlmostEqual(math.exp(audit.log_wealth(0, 0.45, "lower")), lower)

    def test_gamma_one_all_zero_wealth_matches_hypergeometric_probability(self):
        audit = FinitePoolAudit([[0.1] * 10], [0.1] * 10, bets=(1.0,))
        for index in range(3):
            audit.observe(index, 0.0)
        inverse_probability = math.comb(10, 3) / math.comb(8, 3)
        self.assertAlmostEqual(math.exp(audit.log_wealth(0, 0.2, "upper")), inverse_probability)
        self.assertEqual(audit.log_wealth(0, 0.2, "lower"), -math.inf)

    def test_feasible_endpoint_zero_over_zero_has_unit_factor(self):
        zeros = FinitePoolAudit([[0.5, 0.5]], [0.5, 0.5], bets=(1.0,))
        zeros.observe(0, 0)
        self.assertEqual(zeros.log_wealth(0, 0, "lower"), 0.0)
        ones = FinitePoolAudit([[0.5, 0.5]], [0.5, 0.5], bets=(1.0,))
        ones.observe(0, 1)
        self.assertEqual(ones.log_wealth(0, 1, "upper"), 0.0)
        with self.assertRaises(ValueError):
            ones.log_wealth(0, 0, "lower")

    def test_endpoint_factors_stay_one_through_uniform_census(self):
        for loss, direction in [(1, "upper"), (0, "lower")]:
            audit = FinitePoolAudit([[0.1] * 10], [0.1] * 10)
            for index in range(10):
                audit.observe(index, loss)
                self.assertAlmostEqual(audit.log_wealth(0, loss, direction), 0.0, places=13)

    def test_small_remaining_scale_does_not_amplify_endpoint_rounding(self):
        audit = FinitePoolAudit([[0.4997, 0.5, 0.0003]], [1 / 3] * 3)
        for index, loss in enumerate([1, 0, 1]):
            audit.observe(index, loss)
        self.assertTrue(math.isfinite(audit.log_wealth(0, 0.5, "upper")))

    def test_interior_candidate_near_endpoint_preserves_mean_one_wealth(self):
        epsilon = 2 ** -50
        target = [1 - epsilon, epsilon]
        for bets in [(1.0,), DEFAULT_BETS]:
            expected = 0.0
            for index, loss in [(0, 1), (1, 0)]:
                audit = FinitePoolAudit([target], target, bets=bets)
                audit.observe(index, loss)
                expected += target[index] * math.exp(audit.log_wealth(0, 1 - epsilon, "upper"))
            self.assertAlmostEqual(expected, 1.0, places=12)

    def test_directional_wealth_is_monotone_on_identification_domain(self):
        audit = FinitePoolAudit([[0.1, 0.2, 0.3, 0.4]], [0.4, 0.3, 0.2, 0.1])
        audit.observe(0, 0.5)
        audit.observe(2, 1)
        candidates = [0.35 + 0.5 * j / 100 for j in range(101)]
        upper = [audit.log_wealth(0, candidate, "upper") for candidate in candidates]
        lower = [audit.log_wealth(0, candidate, "lower") for candidate in candidates]
        self.assertTrue(all(a <= b + 1e-12 for a, b in zip(upper, upper[1:])))
        self.assertTrue(all(a + 1e-12 >= b for a, b in zip(lower, lower[1:])))


class AnytimeBoundsTests(unittest.TestCase):
    def test_exact_anytime_failure_probability_is_below_delta_on_small_pools(self):
        proposal = [0.25] * 4
        delta = 0.9
        some_failure = False
        for labels in itertools.product([0, 1], repeat=4):
            truth = sum(labels) / 4
            failure_probability = 0.0
            for order in itertools.permutations(range(4)):
                audit = FinitePoolAudit([[0.25] * 4], proposal, delta=delta, bets=(1.0,))
                failed = False
                for index in order:
                    audit.observe(index, labels[index])
                    row = audit.bounds()[0]
                    failed |= row["interval_conflict"] or not (
                        row["lower"] - 1e-12 <= truth <= row["upper"] + 1e-12)
                if failed:
                    failure_probability += order_probability(order, proposal)
            some_failure |= failure_probability > 0
            self.assertLessEqual(failure_probability, delta + 1e-12)
        self.assertTrue(some_failure, "The check must exercise actual sequential exclusions")

    def test_inversion_conservatively_contains_the_accepted_boundary(self):
        audit = FinitePoolAudit([[0.1] * 10], [0.1] * 10, delta=0.2, bets=(1.0,))
        for index in range(5):
            audit.observe(index, 0)
        row = audit.bounds()[0]
        self.assertGreater(row["upper"], 0)
        self.assertLess(row["upper"], row["identification_upper"])
        threshold = math.log(10)
        self.assertGreaterEqual(audit.log_wealth(0, row["upper"], "upper") + 1e-12, threshold)
        self.assertLess(audit.log_wealth(0, row["upper"] - 1e-10, "upper"), threshold)

    def test_census_collapses_every_target_for_fractional_losses(self):
        targets = [[0.1, 0.2, 0.7], [0.5, 0.5, 0.0]]
        losses = [0.25, 0.5, 0.75]
        audit = FinitePoolAudit(targets, [0.4, 0.2, 0.4])
        for index in [2, 0, 1]:
            audit.observe(index, losses[index])
        rows = audit.bounds()
        self.assertEqual(len(rows), 2)
        for row, target in zip(rows, targets):
            expected = math.fsum(a * y for a, y in zip(target, losses))
            self.assertAlmostEqual(row["lower"], expected)
            self.assertEqual(row["lower"], row["upper"])
            self.assertFalse(row["interval_conflict"])
            self.assertEqual(row["label_count"], 3)

    def test_small_remaining_mass_has_valid_partial_intervals(self):
        target = [0.49998, 0.5, 1e-5, 1e-5]
        audit = FinitePoolAudit([target], target)
        for index, loss in [(0, 1), (1, 0), (2, 1)]:
            audit.observe(index, loss)
        row = audit.bounds()[0]
        self.assertFalse(row["interval_conflict"])
        self.assertAlmostEqual(row["identification_lower"], 0.49999)
        self.assertAlmostEqual(row["identification_upper"], 0.5)

    def test_roundoff_does_not_shrink_unqueried_or_all_one_census_endpoints(self):
        target = [0.1630502872777822, 0.09051666499999475, 0.19046823967172433,
                  0.17892107895223147, 0.019839904086117896, 0.027680757808757426,
                  0.04417454819488151, 0.19655398930728965, 0.08879452970122076]
        audit = FinitePoolAudit([target], target)
        self.assertEqual(audit.bounds()[0]["upper"], 1.0)
        for index in range(len(target)):
            audit.observe(index, 1)
        self.assertEqual(audit.bounds()[0]["lower"], 1.0)
        self.assertEqual(audit.bounds()[0]["upper"], 1.0)

    def test_target_depletion_is_exact_before_other_targets_are_known(self):
        audit = FinitePoolAudit([[1, 0, 0], [0, 0.5, 0.5]], [0.5, 0.25, 0.25])
        audit.observe(0, 0.4)
        rows = audit.bounds()
        self.assertEqual((rows[0]["lower"], rows[0]["upper"]), (0.4, 0.4))
        self.assertEqual((rows[1]["lower"], rows[1]["upper"]), (0.0, 1.0))

    def test_partial_identification_uses_weighted_labels_and_missing_mass(self):
        audit = FinitePoolAudit([[0.1, 0.2, 0.7]], [0.4, 0.2, 0.4])
        audit.observe(2, 0.5)
        row = audit.bounds()[0]
        self.assertAlmostEqual(row["identification_lower"], 0.35)
        self.assertAlmostEqual(row["identification_upper"], 0.65)

    def test_empty_acceptance_set_is_explicit_and_has_no_certifiable_upper(self):
        target = [0.005] * 100 + [0.5]
        audit = FinitePoolAudit([target], target)
        for index in range(99):
            audit.observe(index, 0)
        audit.observe(100, 1)
        row = audit.bounds()[0]
        self.assertTrue(row["interval_conflict"])
        self.assertIsNone(row["lower"])
        self.assertIsNone(row["upper"])
        self.assertAlmostEqual(row["identification_lower"], 0.5)
        self.assertAlmostEqual(row["identification_upper"], 0.505)

    def test_input_arrays_are_copied_at_initialization(self):
        target, proposal = [0.5, 0.5], [0.5, 0.5]
        audit = FinitePoolAudit([target], proposal)
        target[0], proposal[0] = 0, 0
        audit.observe(0, 0.4)
        self.assertAlmostEqual(audit.bounds()[0]["identification_lower"], 0.2)


class AnytimeValidationTests(unittest.TestCase):
    def test_invalid_constructor_inputs_fail(self):
        invalid = [([], [1]), ([[1]], []), ([[0.5]], [1]), ([[1, 0]], [1]),
                   ([[1, 0]], [0, 1]), ([[math.nan]], [1]), ([[True]], [1]),
                   ([[1]], [math.inf]), ([[1]], [-1]), ([[1]], [True])]
        for targets, proposal in invalid:
            with self.subTest(targets=targets, proposal=proposal), self.assertRaises(ValueError):
                FinitePoolAudit(targets, proposal)
        for delta in [0, 1, -1, True, math.nan, math.inf]:
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                FinitePoolAudit([[1]], [1], delta=delta)
        for bets in [(), (0,), (-0.1,), (1.1,), (True,), (math.nan,), (0.5, 0.5)]:
            with self.subTest(bets=bets), self.assertRaises(ValueError):
                FinitePoolAudit([[1]], [1], bets=bets)

    def test_duplicate_unsupported_and_invalid_observations_fail_without_mutation(self):
        audit = FinitePoolAudit([[0.5, 0.5, 0]], [0.5, 0.5, 0])
        for index, loss in [(2, 0), (-1, 0), (3, 0), (True, 0), (0.0, 0),
                            (0, -1), (0, 1.1), (0, math.nan), (0, math.inf), (0, False)]:
            with self.subTest(index=index, loss=loss), self.assertRaises(ValueError):
                audit.observe(index, loss)
        self.assertEqual(audit.bounds()[0]["label_count"], 0)
        audit.observe(0, 0)
        with self.assertRaises(ValueError):
            audit.observe(0, 0)
        self.assertEqual(audit.bounds()[0]["label_count"], 1)

    def test_log_wealth_rejects_invalid_targets_directions_and_infeasible_candidates(self):
        audit = FinitePoolAudit([[0.5, 0.5]], [0.5, 0.5])
        audit.observe(0, 1)
        for args in [(0, 0.2, "upper"), (0, math.nan, "upper"), (0, True, "upper"),
                     (1, 0.6, "upper"), (True, 0.6, "upper"), (0, 0.6, "bad")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                audit.log_wealth(*args)

    def test_candidate_tolerance_does_not_use_the_distant_interval_endpoint(self):
        target = [1e-16, 1 - 1e-16]
        audit = FinitePoolAudit([target], target)
        audit.observe(0, 1)
        with self.assertRaises(ValueError):
            audit.log_wealth(0, 0, "lower")

    def test_positive_over_zero_is_never_replaced_by_a_unit_factor(self):
        target = [1e-16, 1 - 1e-16]
        audit = FinitePoolAudit([target], target)
        audit.observe(0, 1e-308)  # Weighted contribution is below float resolution.
        with self.assertRaisesRegex(ValueError, "positive betting numerator"):
            audit.log_wealth(0, 0, "lower")


class UpperCertificateTests(unittest.TestCase):
    def test_deterministic_upper_certificate_does_not_require_two_sided_overlap(self):
        audit = FinitePoolAudit([[1 / 3] * 3], [1e-6, 1e-6, 1 - 2e-6])
        audit.observe(0, 1)
        audit.observe(1, 0)
        self.assertTrue(audit.bounds()[0]["interval_conflict"])
        row = audit.upper_certificates(0.8)[0]
        self.assertTrue(row["upper_test_certified"])
        self.assertIsNone(row["log_wealth"])
        self.assertEqual(row["threshold"], 0.8)
        self.assertEqual(row["target_index"], 0)

    def test_upper_wealth_can_certify_before_deterministic_bounds_do(self):
        audit = FinitePoolAudit([[0.01] * 100], [0.01] * 100)
        for index in range(50):
            audit.observe(index, 0)
        row = audit.upper_certificates(0.1)[0]
        self.assertGreater(row["identification_upper"], 0.1)
        self.assertGreaterEqual(row["log_wealth"], math.log(40))
        self.assertTrue(row["upper_test_certified"])

    def test_known_unsafe_and_unqueried_targets_are_not_certified(self):
        audit = FinitePoolAudit([[1, 0], [0, 1]], [0.5, 0.5])
        self.assertFalse(any(row["upper_test_certified"] for row in audit.upper_certificates(0.1)))
        audit.observe(0, 1)
        rows = audit.upper_certificates(0.1)
        self.assertFalse(rows[0]["upper_test_certified"])
        self.assertIsNone(rows[0]["log_wealth"])
        self.assertFalse(rows[1]["upper_test_certified"])

    def test_invalid_thresholds_fail(self):
        audit = FinitePoolAudit([[1]], [1])
        for threshold in [-0.1, 1.1, True, math.nan, math.inf]:
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                audit.upper_certificates(threshold)


class WeightedOrderTests(unittest.TestCase):
    def test_order_is_reproducible_unique_and_support_restricted(self):
        proposal = [0, 0.2, 0.3, 0.5]
        order = weighted_order(proposal, 32)
        self.assertEqual(set(order), {1, 2, 3})
        self.assertEqual(len(order), 3)
        self.assertEqual(weighted_order(proposal, 32), order)
        self.assertEqual(weighted_order(proposal, 32, 2), order[:2])
        self.assertEqual(weighted_order(proposal, 32, 0), [])

    def test_first_draw_frequencies_follow_proposal(self):
        proposal = [0.5, 0.3, 0.2]
        counts = [0, 0, 0]
        for seed in range(4000):
            counts[weighted_order(proposal, seed, 1)[0]] += 1
        for count, probability in zip(counts, proposal):
            self.assertLess(abs(count / 4000 - probability), 0.03)

    def test_invalid_counts_seeds_and_proposals_fail(self):
        for proposal, seed, count in [([], 0, None), ([0.2, 0.2], 0, None),
                                      ([1], True, None), ([1], 0.1, None),
                                      ([1], 0, True), ([1], 0, -1), ([1], 0, 2)]:
            with self.subTest(proposal=proposal, seed=seed, count=count), self.assertRaises(ValueError):
                weighted_order(proposal, seed, count)


if __name__ == "__main__":
    unittest.main()
