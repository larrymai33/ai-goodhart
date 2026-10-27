import copy
import json
from pathlib import Path
import tempfile
import unittest

from goodhart_audit.unique_io import make_unique_plan, unique_report


class UniqueWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.pools = [
            {'prompt_id': 'p1', 'candidates': [
                {'candidate_id': 'a', 'proxy': 2., 'loss': 1},
                {'candidate_id': 'b', 'proxy': 1., 'loss': 0}]},
            {'prompt_id': 'p2', 'candidates': [
                {'candidate_id': 'c', 'proxy': 2., 'loss': 1},
                {'candidate_id': 'd', 'proxy': 1., 'loss': 0}]}]

    def test_unique_score_only_plan(self):
        for method in ['uniform', 'budget_mixture', 'dyadic_mixture', 'max_uniform', 'envelope']:
            plan = make_unique_plan(self.pools, [1, 2], 4, 8, method=method)
            self.assertEqual(plan, make_unique_plan(self.pools, [1, 2], 4, 8, method=method))
            identities = {(q['prompt_id'], q['candidate_id']) for q in plan['queries']}
            self.assertEqual(len(identities), 4)
            self.assertTrue(all(q['loss'] is None for q in plan['queries']))

    def test_unlabeled_and_partial_prefix_reports(self):
        plan = make_unique_plan(self.pools, [1, 2], 4, 8)
        report = unique_report(self.pools, plan)
        self.assertEqual(report['unique_labels'], 0)
        self.assertTrue(all(row['lower'] == 0 and row['upper'] == 1 for row in report['curve']))
        plan['queries'][0]['loss'] = 0.25
        report = unique_report(self.pools, plan)
        self.assertEqual(report['unique_labels'], 1)
        self.assertEqual(report['draw_count'], 1)
        self.assertTrue(report['anytime_valid'])
        directional = unique_report(self.pools, plan, rule='upper-test')
        self.assertEqual(directional['certification_rule'], 'upper-test')
        self.assertTrue(all(row['certified'] == row['upper_test_certified'] for row in directional['curve']))

    def test_out_of_order_labels_and_plan_tampering_rejected(self):
        plan = make_unique_plan(self.pools, [1, 2], 4, 8)
        plan['queries'][1]['loss'] = 0
        with self.assertRaisesRegex(ValueError, 'prefix|order'):
            unique_report(self.pools, plan)
        plan = make_unique_plan(self.pools, [1, 2], 4, 8)
        plan['queries'].reverse()
        with self.assertRaisesRegex(ValueError, 'plan|order'):
            unique_report(self.pools, plan)

    def test_census_exact_and_source_labels_ignored(self):
        plan = make_unique_plan(self.pools, [1, 2], 4, 8)
        for query in plan['queries']:
            query['loss'] = 1 if query['rank'] == 0 else 0
        report = unique_report(self.pools, plan, threshold=0.6)
        self.assertEqual(report['certified_budgets'], [1])
        self.assertAlmostEqual(report['curve'][0]['lower'], 0.5)
        self.assertAlmostEqual(report['curve'][0]['upper'], 0.5)
        self.assertAlmostEqual(report['curve'][1]['lower'], 1)
        changed = copy.deepcopy(self.pools)
        for pool in changed:
            for candidate in pool['candidates']:
                candidate['loss'] = 0
        self.assertEqual(report, unique_report(changed, plan, threshold=0.6))

    def test_cli_unique_roundtrip(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            pool_path, plan_path, report_path = [path / name for name in ['pool.jsonl', 'plan.json', 'report.json']]
            pool_path.write_text('\n'.join(json.dumps(row) for row in self.pools))
            args = [sys.executable, '-m', 'goodhart_audit']
            result = subprocess.run(args + ['plan-unique', '--pool', str(pool_path), '--out', str(plan_path),
                '--labels', '4', '--seed', '8', '--budgets', '1,2'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(plan_path.read_text())
            plan['queries'][0]['loss'] = 0
            plan_path.write_text(json.dumps(plan))
            result = subprocess.run(args + ['report-unique', '--pool', str(pool_path), '--audit', str(plan_path),
                '--out', str(report_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report_path.read_text())['unique_labels'], 1)


if __name__ == '__main__':
    unittest.main()
