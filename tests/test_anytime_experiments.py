import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
try:
    import numpy as np
except ImportError:
    raise unittest.SkipTest('Optional anytime experiment tests need existing NumPy.')

from experiments.run_anytime_study import race_orders, simulate_paths, _update, _logmean, run
from goodhart_audit.anytime import DEFAULT_BETS, FinitePoolAudit
from goodhart_audit.core import rank_weights


class AnytimeExperimentTests(unittest.TestCase):
    def test_race_orders_have_no_repeats(self):
        uniforms = np.random.default_rng(7).random((10, 12))
        orders = race_orders(np.array([0.2, 0.3, 0.5]), 4, uniforms)
        self.assertEqual(orders.shape, (10, 12))
        for order in orders:
            self.assertEqual(len(set(order)), 12)
        np.testing.assert_array_equal(orders, race_orders(np.array([0.2, 0.3, 0.5]), 4, uniforms))

    def test_vectorized_wealth_matches_scalar_engine(self):
        p, m = 3, 4
        loss = np.array([[0, 0.2, 1, 0], [0.5, 0, 1, 0], [1, 0.3, 0, 1.]])
        weights = np.array([rank_weights(m, n) for n in [1, 2, 4]])
        q = np.array([0.4, 0.3, 0.2, 0.1])
        order = race_orders(q, p, np.random.default_rng(8).random((1, p*m)))
        rows = simulate_paths(loss, weights, q, order, [1, 3, 6, 12], 0.05, 0.4,
                              DEFAULT_BETS, diagnostics=True)
        engine = FinitePoolAudit([np.tile(w / p, p).tolist() for w in weights],
                                 np.tile(q / p, p).tolist(), delta=0.05)
        truth = weights @ loss.mean(axis=0)
        for t, index in enumerate(order[0], 1):
            engine.observe(int(index), float(loss.flat[index]))
            if t not in [1, 3, 6, 12]:
                continue
            row = next(row for row in rows if row['labels'] == t)
            for n in range(len(weights)):
                for direction in ['upper', 'lower']:
                    actual = engine.log_wealth(n, float(truth[n]), direction)
                    measured = row['diagnostics']['log_' + direction + '_truth'][n]
                    self.assertAlmostEqual(actual, measured, places=9)

    def test_all_safe_eventual_census_is_exact_and_certified(self):
        loss = np.zeros((2, 4))
        weights = np.array([rank_weights(4, n) for n in [1, 2, 4]])
        q = np.ones(4) / 4
        order = race_orders(q, 2, np.random.default_rng(4).random((2, 8)))
        rows = simulate_paths(loss, weights, q, order, [1, 8], 0.05, 0.1, DEFAULT_BETS)
        for row in rows:
            self.assertFalse(row['ever_miscoverage'])
            self.assertFalse(row['ever_false_certification'])
            if row['labels'] == 8:
                self.assertEqual(row['certified_count'], 3)
                self.assertIsNotNone(row['first_full_budget_certified'])

    def test_unsafe_target_is_not_counted_as_censored_success(self):
        loss = np.ones((2, 4))
        weights = np.array([rank_weights(4, n) for n in [1, 4]])
        q = np.ones(4) / 4
        rows = simulate_paths(loss, weights, q, np.arange(8).reshape(1, 8), [8], 0.05, 0.1, DEFAULT_BETS)
        self.assertIsNone(rows[0]['first_full_budget_certified'])
        self.assertEqual(rows[0]['certified_count'], 0)

    def test_tiny_remaining_mass_still_updates_wealth(self):
        loss = np.array([[0., 0., 1.]])
        weights = np.array([[1 - 2e-14, 1e-14, 1e-14]])
        q = np.ones(3) / 3
        rows = simulate_paths(loss, weights, q, np.array([[0, 1, 2]]),
                              [2, 3], 0.05, 0.1, DEFAULT_BETS, diagnostics=True)
        engine = FinitePoolAudit(weights.tolist(), q.tolist())
        engine.observe(0, 0)
        engine.observe(1, 0)
        self.assertAlmostEqual(rows[0]['diagnostics']['log_upper_truth'][0],
                               engine.log_wealth(0, 1e-14, 'upper'), places=12)

    def test_positive_over_zero_is_never_a_unit_factor(self):
        logs = np.zeros((1, 1, 2))
        with self.assertRaises(ArithmeticError):
            _update(logs, np.array([[1e-12]]), np.array([[0.]]),
                    np.array([[True]]), np.array([1., .5]))

    def test_zero_wealth_has_negative_infinite_log_not_nan(self):
        result = _logmean(np.array([[[-np.inf]]]))
        self.assertTrue(np.isneginf(result[0, 0]))

    def test_all_one_census_preserves_true_endpoint_wealth(self):
        loss = np.ones((3, 8))
        weights = np.array([rank_weights(8, n) for n in [1, 2, 4, 8]])
        q = np.ones(8) / 8
        order = race_orders(q, 3, np.random.default_rng(32).random((1, 24)))
        rows = simulate_paths(loss, weights, q, order, [24], 0.05, 0.1, DEFAULT_BETS, diagnostics=True)
        # Target 0 has Y=m=1 at every step under uniform acquisition.
        self.assertAlmostEqual(rows[0]['diagnostics']['log_upper_truth'][0], 0, places=10)

    def test_source_change_during_measurement_rejects_manifest(self):
        config = json.loads(Path('experiments/anytime_protocol.json').read_text())
        config.update(prompts=32, pool_size=16, budgets=[1, 2, 4, 8, 16],
                      label_checkpoints=[2], max_labels=2, replicates=2,
                      scenarios=['all_safe'], methods=['uniform'])
        with tempfile.TemporaryDirectory() as folder:
            with patch('experiments.run_anytime_study.source_hashes', side_effect=[{'source': 'before'}, {'source': 'after'}]):
                with self.assertRaisesRegex(RuntimeError, 'sources changed'):
                    run(config, Path(folder), draw_plots=False)
            self.assertFalse((Path(folder) / 'manifest.json').exists())

    def test_near_endpoint_vectorized_wealth_preserves_mean_one(self):
        epsilon = 2 ** -50
        weights = np.array([[1 - epsilon, epsilon]])
        q = weights[0]
        for bets in [(1.,), DEFAULT_BETS]:
            rows = simulate_paths(np.array([[1., 0.]]), weights, q,
                np.array([[0, 1], [1, 0]]), [1], .05, .1, bets, diagnostics=True)
            expectation = sum(q[row['replicate']] * np.exp(row['diagnostics']['log_upper_truth'][0])
                              for row in rows)
            self.assertAlmostEqual(expectation, 1, places=12)

    def test_directional_certification_matches_public_rule_at_every_prefix(self):
        loss = np.array([[1., 0., 0.]])
        weights = np.array([[1/3, 1/3, 1/3]])
        q = np.array([1e-6, 1e-6, 1-2e-6])
        rows = simulate_paths(loss, weights, q, np.array([[0, 1, 2]]),
                              [1, 2, 3], .05, .8, DEFAULT_BETS)
        engine = FinitePoolAudit(weights.tolist(), q.tolist())
        for t in range(3):
            engine.observe(t, float(loss[0, t]))
            expected = int(engine.upper_certificates(.8)[0]['upper_test_certified'])
            self.assertEqual(rows[t]['certified_count'], expected)
            if t == 1:
                self.assertTrue(engine.bounds()[0]['interval_conflict'])
                self.assertEqual(expected, 1)

    def test_impossible_threshold_is_excluded_before_betting_division(self):
        loss = np.array([[0.9929582154957468, 0.3203006687935771,
                          0.406688968044865, 0.31754068251260315]])
        weights = np.array([rank_weights(4, n) for n in [1, 2, 4]])
        q = np.ones(4) / 4
        order = np.array([[2, 3, 0, 1]])
        rows = simulate_paths(loss, weights, q, order, [1, 2, 3, 4], .05, 1., DEFAULT_BETS)
        self.assertTrue(all(row['certified_count'] == 3 for row in rows))


if __name__ == '__main__':
    unittest.main()
