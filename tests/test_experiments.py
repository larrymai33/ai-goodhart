import unittest
import json
from pathlib import Path
import tempfile

try:
    import numpy as np
except ImportError:
    raise unittest.SkipTest('Optional experiment tests require existing NumPy; core tests do not.')

from experiments.run_study import make_scenarios, proposals, evaluate_draws, wilson, run
from goodhart_audit.core import rank_weights, estimate_risk


class ExperimentTests(unittest.TestCase):
    def test_scenario_exact_truth(self):
        scenarios = make_scenarios(128, 32, 4)
        weights = np.array([rank_weights(32, n) for n in [1, 2, 16, 32]])
        np.testing.assert_allclose(weights @ scenarios['top_failure'].mean(axis=0),
                                   np.array([1, 2, 16, 32]) / 32)
        np.testing.assert_allclose(weights @ scenarios['flat_risk'].mean(axis=0), 0.125)
        np.testing.assert_allclose(weights @ scenarios['prompt_cluster'].mean(axis=0), 0.0625)

    def test_every_proposal_has_support_and_normalizes(self):
        for q in proposals(32, [1, 2, 4, 8, 16, 32]).values():
            self.assertTrue(np.all(q > 0))
            self.assertAlmostEqual(q.sum(), 1)

    def test_all_zero_observations_do_not_prove_zero_risk(self):
        loss = np.array([[1., 0.]])
        weights = np.array([rank_weights(2, 1), rank_weights(2, 2)])
        result = evaluate_draws(loss, weights, np.array([0.5, 0.5]),
                                np.zeros(20, dtype=int), np.ones(20, dtype=int), 0.05, 0.1)
        self.assertGreater(result['upper'][1], 0)
        self.assertEqual(result['naive_upper'][1], 0)
        self.assertFalse(result['false_certification'])
        self.assertTrue(result['naive_false_certification'])

    def test_full_observation_partial_bounds_collapse(self):
        loss = np.array([[1., 0.]])
        weights = np.array([rank_weights(2, 1), rank_weights(2, 2)])
        result = evaluate_draws(loss, weights, np.array([0.5, 0.5]),
                                np.zeros(4, dtype=int), np.array([0, 1, 0, 1]), 0.05, 0.1)
        np.testing.assert_allclose(result['identification_lower'], [0.5, 1])
        np.testing.assert_allclose(result['identification_upper'], [0.5, 1])

    def test_wilson_reports_uncertainty_at_perfect_coverage(self):
        lo, hi = wilson(200, 200)
        self.assertLess(lo, 1)
        self.assertAlmostEqual(hi, 1)

    def test_vectorized_experiment_matches_public_estimator(self):
        rng = np.random.default_rng(13)
        loss = rng.random((4, 16))
        budgets = [1, 2, 8, 16]
        weights = np.array([rank_weights(16, n) for n in budgets])
        for q in proposals(16, budgets).values():
            ranks = rng.choice(16, 200, p=q)
            prompts = rng.integers(0, 4, 200)
            vector = evaluate_draws(loss, weights, q, prompts, ranks, 0.05, 0.1)
            scalar = estimate_risk(ranks.tolist(), loss[prompts, ranks].tolist(),
                                   q.tolist(), budgets, 0.05)
            for field in ['estimate', 'lower', 'upper']:
                np.testing.assert_allclose(vector[field], [s[field] for s in scalar], atol=1e-12)

    def test_run_honors_configured_methods(self):
        config = json.loads(Path('experiments/protocol.json').read_text())
        config.update(prompts=32, pool_size=16, budgets=[1, 2, 4, 8, 16],
                      draw_counts=[2], replicates=2, scenarios=['all_safe'], methods=['uniform'])
        with tempfile.TemporaryDirectory() as folder:
            rows = run(config, Path(folder), plots=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['method'], 'uniform')

    def test_manifest_excludes_figures_not_emitted_by_current_run(self):
        config = json.loads(Path('experiments/protocol.json').read_text())
        config.update(prompts=32, pool_size=16, budgets=[1, 2, 4, 8, 16],
                      draw_counts=[2], replicates=2, scenarios=['all_safe'], methods=['uniform'])
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / 'coverage.svg').write_text('<svg>stale</svg>')
            run(config, out, plots=False)
            manifest = json.loads((out / 'manifest.json').read_text())
        self.assertNotIn('coverage.svg', manifest['outputs_sha256'])

    def test_study_rejects_grid_without_baseline_before_writing_outputs(self):
        config = json.loads(Path('experiments/protocol.json').read_text())
        config.update(prompts=32, pool_size=16, budgets=[2, 4, 8, 16],
                      draw_counts=[2], replicates=2, scenarios=['all_safe'], methods=['uniform'])
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'run'
            with self.assertRaisesRegex(ValueError, 'budget.*1|baseline'):
                run(config, out, plots=False)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
