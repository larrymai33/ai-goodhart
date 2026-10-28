"""Exact audit-budget checks and one optional matched-budget tensor case."""
from fractions import Fraction as F
from importlib.util import find_spec
from itertools import product
import unittest

from experiments.check_audit_budget import compare_training, hazards, moments, verify


class AuditBudgetTests(unittest.TestCase):
    def test_sharp_and_equal_time_schedules_have_same_cost(self):
        sharp = hazards(F(1, 2), 3, 'inverse_survival')
        equal = hazards(F(1, 2), 3, 'equal_time')
        self.assertEqual(sharp, (F(1, 4), F(1, 5), F(1, 6)))
        self.assertEqual(equal, tuple(reversed(sharp)))
        for qs, expected in [(sharp, 9), (equal, F(31, 3))]:
            result = moments(qs)
            self.assertEqual(result['purchase_probability'], F(1, 2))
            self.assertEqual(result['sum_step_mse'], expected)
            self.assertEqual(result['summed_error_mse'], expected)

    def test_first_query_enumeration_matches_full_bernoulli_path_enumeration(self):
        for kind in ['inverse_survival', 'equal_time']:
            qs = hazards(F(2, 5), 4, kind)
            means, matrix = [F(0)]*4, [[F(0) for _ in qs] for _ in qs]
            for draws in product([0, 1], repeat=4):
                probability = F(1)
                known, errors = False, []
                for z, q in zip(draws, qs):
                    probability *= q if z else 1-q
                    estimate = F(1) if known else z/q
                    errors.append(estimate-1)
                    known = known or bool(z)
                for i in range(4):
                    means[i] += probability*errors[i]
                    for j in range(4):
                        matrix[i][j] += probability*errors[i]*errors[j]
            result = moments(qs)
            self.assertEqual(result['mean_errors'], tuple(means))
            self.assertEqual(result['error_cross_moments'], tuple(map(tuple, matrix)))
            self.assertEqual(means, [0]*4)
            self.assertTrue(all(matrix[i][j] == 0 for i in range(4) for j in range(4) if i != j))

    def test_optimal_schedule_average_is_one_shot_estimator_for_every_query_time(self):
        for T, p in product(range(1, 7), [F(1, 10), F(1, 2), F(9, 10)]):
            for j, q in enumerate(hazards(p, T, 'inverse_survival')):
                self.assertEqual((1/q+(T-1-j))/T, 1/p)

    def test_arbitrary_miss_baseline_cannot_beat_two_point_lower_bound(self):
        for p, baseline in product([F(1, 10), F(1, 2), F(9, 10)], [-3, -1, 0, 1, 3]):
            risks = []
            for y in [-1, 1]:
                hit = (y-(1-p)*baseline)/p
                self.assertEqual((1-p)*baseline+p*hit, y)
                risks.append((1-p)*(baseline-y)**2+p*(hit-y)**2)
            self.assertGreaterEqual(max(risks), (1-p)/p)
            self.assertEqual(max(risks) == (1-p)/p, baseline == 0)

    def test_reused_draw_has_nonzero_error_cross_moments(self):
        p, T = F(1, 2), 3
        step = (1-p)*1+p*(1/p-1)**2
        summed = (1-p)*T*T+p*(T/p-T)**2
        self.assertEqual(step*T, 3)
        self.assertEqual(summed, 9)
        self.assertNotEqual(step*T, summed)

    def test_exact_grid_and_nonuniform_allocations(self):
        result = verify()
        self.assertEqual(result['schedule_cases'], 180)
        self.assertEqual(result['allocation_cases'], 192)

    def test_invalid_inputs_fail_without_silent_coercion(self):
        for p, T in [(0, 3), (1, 3), (F(1, 2), 0), (F(1, 2), True), (0.5, 3)]:
            with self.assertRaises((TypeError, ValueError)):
                hazards(p, T, 'inverse_survival')
        with self.assertRaises(ValueError):
            hazards(F(1, 2), 3, 'unknown')
        for qs in [(), (0,), (1,), (0.5,), (True,)]:
            with self.assertRaises((TypeError, ValueError)):
                moments(qs)

    @unittest.skipUnless(find_spec('torch') is not None, 'optional installed PyTorch comparison')
    def test_matched_budget_comparison_keeps_conditional_and_marginal_errors_separate(self):
        result = compare_training(learning_rates=(0.2,), budgets=((F(1, 2), F(1, 4)),))
        methods = result['settings'][0]['methods']
        for name, record in methods.items():
            self.assertEqual(record['expected_distinct_labels'], '9/4')
            if name != 'reuse':
                self.assertLess(max(record['conditional_bias_squared']), 1e-24)
                self.assertAlmostEqual(record['summed_error_mse'], sum(record['gradient_mse']), places=11)
                self.assertEqual(record['leaves'], 16)
        self.assertGreater(max(methods['reuse']['conditional_bias_squared'][1:]), 1e-6)
        self.assertEqual(methods['reuse']['leaves'], 4)


if __name__ == '__main__':
    unittest.main()
