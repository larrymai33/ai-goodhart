"""Audit lifecycle regressions; the tensor experiment is optional."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from importlib.util import find_spec
import unittest

from experiments.check_audit_cache import AuditCache, microbatch_example, verify_training_loop


class AuditCacheTests(unittest.TestCase):
    def test_weight_is_frozen_across_chunks_and_changes_at_next_update(self):
        cache, calls = AuditCache(), []
        labels = [-1, 1]
        cache.begin_update({'a': F(1, 4)}, lambda g, q: calls.append((g, q)) or True,
                           lambda g: labels)
        first = cache.decision('a')
        labels[0] = 123  # cached targets must not alias a mutable label list
        self.assertEqual(first.full_advantages, (-1.0, 1.0))
        self.assertEqual(first.weight, 4)
        self.assertIs(cache.decision('a'), first)
        self.assertEqual(calls, [('a', F(1, 4))])
        self.assertEqual(cache.purchases, 1)
        with self.assertRaises(FrozenInstanceError):
            first.weight = 1
        cache.end_update()

        def forbidden(*args):
            self.fail('cached groups must not draw or purchase again')
        cache.begin_update({'a': F(1, 4)}, forbidden, forbidden)
        self.assertEqual(cache.decision('a').weight, 1)
        self.assertEqual(cache.decision('a').full_advantages, (-1.0, 1.0))
        self.assertEqual(cache.purchases, 1)
        cache.end_update()

    def test_unselected_group_gets_a_fresh_draw_only_next_update(self):
        cache, draws = AuditCache(), []
        cache.begin_update({'a': F(1, 2)}, lambda g, q: draws.append(g) or False,
                           lambda g: self.fail('unselected audit called'))
        self.assertIsNone(cache.decision('a').full_advantages)
        self.assertEqual(cache.decision('a').weight, 0)
        self.assertEqual(cache.decision('a').weight, 0)
        self.assertEqual(draws, ['a'])
        cache.end_update()
        cache.begin_update({'a': F(1, 2)}, lambda g, q: draws.append(g) or True,
                           lambda g: [-1, 1])
        self.assertEqual(draws, ['a', 'a'])
        self.assertEqual(cache.decision('a').weight, 2)
        cache.end_update()

    def test_exact_premature_cache_switch_has_biased_mean(self):
        result = microbatch_example()
        self.assertEqual(result['full_gradient'], 2)
        self.assertEqual(result['frozen_update_weight_mean'], 2)
        self.assertEqual(result['premature_cache_switch_mean'], F(5, 4))
        self.assertEqual(result['expected_group_purchases'], F(1, 4))

    def test_lifecycle_and_sampling_design_errors_fail_explicitly(self):
        cache = AuditCache()
        for action in [lambda: cache.decision('a'), cache.end_update]:
            with self.assertRaises(RuntimeError):
                action()
        for q in [0, -1, 2, 0.5, True]:
            with self.assertRaises((TypeError, ValueError)):
                cache.begin_update({'a': q}, lambda *args: False, lambda g: [0])
        with self.assertRaises(TypeError):
            cache.begin_update({'a': F(1, 2)}, lambda *args: 1, lambda g: [0])
        for labels in [[], [float('nan')], [float('inf')], [True]]:
            with self.assertRaises((TypeError, ValueError)):
                AuditCache().begin_update({'a': 1}, lambda *args: True, lambda g: labels)
        cache.begin_update({'a': 1}, lambda *args: True, lambda g: [0])
        with self.assertRaises(RuntimeError):
            cache.begin_update({'a': 1}, lambda *args: True, lambda g: [0])
        with self.assertRaises(KeyError):
            cache.decision('absent')
        cache.end_update()

    @unittest.skipUnless(find_spec('torch') is not None, 'optional installed PyTorch experiment')
    def test_enumerated_training_loop_recovers_each_conditional_gradient(self):
        result = verify_training_loop()
        self.assertEqual(result['optimizer_updates_per_path'], 3)
        self.assertEqual(result['leaves'], 16)
        self.assertEqual(result['expected_distinct_labels'], '279/64')
        self.assertGreater(result['clipping_active_states'], 0)
        self.assertLess(result['maximum_conditional_gradient_error'], 1e-12)
        self.assertLess(result['maximum_conditional_objective_error'], 1e-12)
        self.assertLess(result['maximum_partition_gradient_error'], 1e-12)
        self.assertLess(result['maximum_finite_difference_error'], 1e-8)


if __name__ == '__main__':
    unittest.main()
