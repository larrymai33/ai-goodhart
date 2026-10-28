"""Independent finite checks of the program-audit benchmark, not LLM data."""
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement, permutations, product
from math import prod
import unittest

from experiments.check_program_audit import miss_probability, singleton_zero_cost, zero_cost


def brute_prior_miss(profile, c, b, d):
    """Enumerate hidden bad rows and failure positions, with fixed query sets."""
    misses = total = 0
    for bad_rows in combinations(range(len(profile)), b):
        for failures in product(list(combinations(range(c), d)), repeat=b):
            total += 1
            misses += all(all(j >= profile[i] for j in failed)
                          for i, failed in zip(bad_rows, failures))
    return F(misses, total)


def brute_policy_miss(profile, matrix):
    """Enumerate row permutations and queried column subsets on a fixed table."""
    probability = F(0)
    orders = list(permutations(profile))
    for order in orders:
        factors = []
        for k, row in zip(order, matrix):
            subsets = list(combinations(range(len(row)), k))
            factors.append(F(sum(all(row[j] == 0 for j in subset) for subset in subsets),
                             len(subsets)))
        probability += prod(factors)
    return probability / len(orders)


class ProgramAuditTests(unittest.TestCase):
    def test_miss_formula_matches_enumerated_hidden_tables(self):
        for c, N in [(2, 3), (3, 3)]:
            for b in range(1, N + 1):
                for d in range(1, c + 1):
                    for profile in combinations_with_replacement(range(c + 1), N):
                        self.assertEqual(miss_probability(profile, c, b, d),
                                         brute_prior_miss(profile, c, b, d))

    def test_single_failure_closed_form_matches_allocation_lp(self):
        for N, c in product(range(1, 5), repeat=2):
            for b in range(1, N + 1):
                for delta in [F(0), F(1, 20), F(1, 4), F(1, 2), F(1)]:
                    self.assertEqual(zero_cost(N, c, b, delta)[0],
                                     singleton_zero_cost(N, c, b, delta))
        self.assertEqual(singleton_zero_cost(7, 5, 1, F(1, 20)), F(133, 4))
        self.assertEqual(singleton_zero_cost(4, 4, 2, F(1, 4)), F(7))
        self.assertEqual(singleton_zero_cost(100, 20, 6, F(1, 20)), F(239936300, 313113))

    def test_dense_failures_make_partial_inspection_strictly_better(self):
        cost, mixture = zero_cost(2, 4, 1, F(1, 4), d=2)
        self.assertEqual(cost, F(7, 2))
        self.assertEqual(sum(weight for weight, _ in mixture), 1)
        self.assertEqual(sum(weight * sum(profile) for weight, profile in mixture), cost)
        self.assertEqual(sum(weight * miss_probability(profile, 4, 1, 2)
                             for weight, profile in mixture), F(1, 4))
        # Completing a row needs three passing tests under the d=2 promise.
        complete_rows_cost = 3 * singleton_zero_cost(2, 1, 1, F(1, 4))
        self.assertEqual(complete_rows_cost, F(9, 2))
        self.assertLess(cost, complete_rows_cost)

    def test_mixture_is_valid_for_every_small_promised_unsafe_table(self):
        N, c, b, d, delta = 2, 3, 1, 2, F(1, 4)
        _, mixture = zero_cost(N, c, b, delta, d)
        rows = [row for row in product((0, 1), repeat=c) if sum(row) == 0 or sum(row) >= d]
        maximum = F(0)
        for matrix in product(rows, repeat=N):
            if sum(any(row) for row in matrix) < b:
                continue
            p = sum(weight * brute_policy_miss(profile, matrix) for weight, profile in mixture)
            self.assertLessEqual(p, delta)
            maximum = max(maximum, p)
        self.assertEqual(maximum, delta)

    def test_density_promise_cannot_be_silently_dropped(self):
        _, mixture = zero_cost(2, 4, 1, F(1, 4), d=2)
        singleton_table = ((1, 0, 0, 0), (0, 0, 0, 0))
        actual_error = sum(w * brute_policy_miss(p, singleton_table) for w, p in mixture)
        self.assertEqual(actual_error, F(9, 16))
        self.assertGreater(actual_error, F(1, 4))

    def test_hull_cost_matches_exhaustive_two_point_mixtures(self):
        for N, c, b, d in [(3, 3, 2, 2), (3, 4, 1, 2), (2, 4, 2, 3)]:
            points = [(sum(p), brute_prior_miss(p, c, b, d))
                      for p in combinations_with_replacement(range(c + 1), N)]
            for delta in [F(1, 20), F(1, 3), F(4, 5)]:
                candidates = [F(cost) for cost, risk in points if risk <= delta]
                for (cost1, risk1), (cost2, risk2) in combinations(points, 2):
                    if risk1 == risk2 or not min(risk1, risk2) <= delta <= max(risk1, risk2):
                        continue
                    weight = (delta - risk2) / (risk1 - risk2)
                    candidates.append(weight * cost1 + (1 - weight) * cost2)
                self.assertEqual(zero_cost(N, c, b, delta, d)[0], min(candidates))

    def test_invalid_inputs_and_large_enumerations_are_rejected(self):
        for args in [(0, 3, 1, F(1, 4)), (2, True, 1, F(1, 4)),
                     (2, 3, 3, F(1, 4)), (2, 3, 1, 0.25), (2, 3, 1, F(-1)),
                     (2, 3, 1, F(1, 4), 4), (20, 20, 1, F(1, 4))]:
            with self.subTest(args=args), self.assertRaises((TypeError, ValueError)):
                zero_cost(*args)
        for args in [([], 3, 1), ([True], 3, 1), ([4], 3, 1), ([-1], 3, 1)]:
            with self.subTest(args=args), self.assertRaises((TypeError, ValueError)):
                miss_probability(*args)


if __name__ == '__main__':
    unittest.main()
