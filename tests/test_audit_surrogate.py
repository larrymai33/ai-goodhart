"""Exact functional checks, with no model or optimizer package dependency."""
from fractions import Fraction as F
from itertools import product
from importlib.util import find_spec
import unittest

from experiments.check_audit_surrogate import (
    correction, positive_gap, ratio_gradient, reuse_example, surrogate, verify_autograd,
)


class AuditSurrogateTests(unittest.TestCase):
    @unittest.skipUnless(find_spec('torch') is not None, 'optional installed PyTorch check')
    def test_actual_autograd_matches_exact_reference_and_reuse_counterexample(self):
        result = verify_autograd()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['fixed_ratio_cases'], 400)
        self.assertLess(result['maximum_absolute_error'], 1e-12)
        self.assertAlmostEqual(result['reused_second_expected_gradient'], -48/25, places=12)
        self.assertAlmostEqual(result['full_at_visited_expected_gradient'], -49/25, places=12)

    def test_audit_advantage_is_unbiased_but_clipped_loss_is_not(self):
        q, e, r = F(1, 4), F(1, 5), F(3, 2)
        audited = correction(1, -1, q, 1)
        self.assertEqual(audited, -7)
        self.assertEqual((1-q)*1 + q*audited, -1)
        self.assertEqual((1-q)*surrogate(r, 1, e) + q*surrogate(r, audited, e), F(-69, 40))
        self.assertEqual(surrogate(r, -1, e), F(-3, 2))
        self.assertEqual((1-q)*ratio_gradient(r, 1, e) + q*ratio_gradient(r, audited, e), F(-7, 4))
        self.assertEqual(ratio_gradient(r, -1, e), -1)

    def test_exact_gap_law_on_all_clip_regions_and_signs(self):
        for weak, full, q, r in product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2],
                                      [F(1, 10), F(1, 4), F(1, 2), F(1)],
                                      [F(1, 2), F(4, 5), F(1), F(6, 5), F(3, 2), F(2)]):
            e = F(1, 5)
            audited = correction(weak, full, q, 1)
            direct = (1-q)*surrogate(r, weak, e) + q*surrogate(r, audited, e)
            gap = positive_gap(weak, full, q)
            distance = max(1-e-r, r-1-e, F(0))
            self.assertGreaterEqual(gap, 0)
            self.assertEqual(direct, surrogate(r, full, e) - distance*gap)
            self.assertEqual(gap, ((1-q)*abs(weak) + abs(full-(1-q)*weak) - abs(full))/2)

    def test_correction_after_loss_and_gradient_recovers_target(self):
        for weak, full, q, r in product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2],
                                      [F(1, 4), F(1, 2), F(1)],
                                      [F(1, 2), F(1), F(3, 2)]):
            for function in [surrogate, ratio_gradient]:
                w, f = function(r, weak, F(1, 5)), function(r, full, F(1, 5))
                self.assertEqual((1-q)*w + q*correction(w, f, q, 1), f)

    def test_ratio_derivative_matches_independent_finite_difference(self):
        h, e = F(1, 10000), F(1, 5)
        for r, a in product([F(1, 2), F(1), F(3, 2)], [-3, 0, 2]):
            numerical = (surrogate(r+h, a, e) - surrogate(r-h, a, e))/(2*h)
            self.assertEqual(ratio_gradient(r, a, e), numerical)

    def test_reused_audit_bias_occurs_without_active_ratio_clipping(self):
        result = reuse_example()
        self.assertEqual(result['first_expected_gradient'], -2)
        self.assertEqual(result['reused_second_expected_gradient'], F(-48, 25))
        self.assertEqual(result['full_at_visited_expected_gradient'], F(-49, 25))
        self.assertEqual(result['fresh_or_cached_second_expected_gradient'], F(-49, 25))
        self.assertEqual(result['expected_distinct_group_audits'], F(3, 4))
        self.assertTrue(all(F(4, 5) < r < F(6, 5) for r in result['second_ratios']))
        # Independent central differentiation through a valid two-action policy.
        for theta in [F(1), F(24, 25)]:
            def full_objective(t):
                return (surrogate(t*t, -1, F(1, 5))
                        + surrogate(2-t*t, 1, F(1, 5)))/2
            h = F(1, 100000)
            derivative = (full_objective(theta+h)-full_objective(theta-h))/(2*h)
            self.assertEqual(derivative, -2*theta)

    def test_validation_does_not_silently_coerce_inputs_or_kinks(self):
        for args in [(1, 1, 0), (1, 1, F(1)), (0, 1, F(1, 5)),
                     (1.0, 1, F(1, 5)), (1, True, F(1, 5))]:
            with self.assertRaises((TypeError, ValueError)):
                surrogate(*args)
        for q, z in [(0, 1), (F(2), 1), (0.5, 1), (F(1, 2), True), (F(1, 2), 2)]:
            with self.assertRaises((TypeError, ValueError)):
                correction(1, -1, q, z)
        for r in [F(4, 5), F(6, 5)]:
            with self.assertRaises(ValueError):
                ratio_gradient(r, 1, F(1, 5))


if __name__ == '__main__':
    unittest.main()
