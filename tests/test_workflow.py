import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from goodhart_audit.io import load_pool, make_plan, audit_report


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'pool.jsonl'
        self.rows = [
            {'prompt_id': 'p1', 'candidates': [
                {'candidate_id': 'b', 'proxy': 1, 'loss': 0, 'text': 'B'},
                {'candidate_id': 'a', 'proxy': 1, 'loss': 1, 'text': 'A'}]},
            {'prompt_id': 'p2', 'candidates': [
                {'candidate_id': 'c', 'proxy': 2, 'loss': 1},
                {'candidate_id': 'd', 'proxy': 0, 'loss': 0}]}]
        self.write_rows()

    def write_rows(self):
        self.path.write_text('\n'.join(json.dumps(x) for x in self.rows), encoding='utf-8')

    def test_plan_reproducible_and_never_reveals_hidden_labels(self):
        pool = load_pool(self.path)
        plan = make_plan(pool, [1, 2], 20, 7)
        self.assertEqual(plan, make_plan(pool, [1, 2], 20, 7))
        self.assertTrue(all(q['loss'] is None for q in plan['queries']))
        self.assertEqual(pool[0]['candidates'][0]['candidate_id'], 'a')
        self.assertEqual(len(plan['draws']), 20)
        self.assertLessEqual(len(plan['queries']), 4)

    def labeled_plan(self):
        pool = load_pool(self.path)
        plan = make_plan(pool, [1, 2], 50, 7)
        labels = {(p['prompt_id'], c['candidate_id']): c['loss']
                  for p in self.rows for c in p['candidates']}
        for q in plan['queries']:
            q['loss'] = labels[q['prompt_id'], q['candidate_id']]
        return pool, plan

    def test_full_labels_collapse_identification_and_report_exact_risk(self):
        pool, plan = self.labeled_plan()
        report = audit_report(pool, plan, delta=0.05, threshold=0.6)
        self.assertEqual(report['unique_labels'], 4)
        self.assertEqual(report['draw_count'], 50)
        self.assertEqual(report['estimand'], 'conditional_finite_pool')
        self.assertAlmostEqual(report['curve'][0]['identification_lower'], 0.5)
        self.assertAlmostEqual(report['curve'][0]['identification_upper'], 0.5)
        self.assertAlmostEqual(report['curve'][1]['identification_lower'], 1)
        self.assertEqual(report['certified_budgets'], [1])

    def test_missing_labels_fail(self):
        pool = load_pool(self.path)
        plan = make_plan(pool, [1, 2], 20, 7)
        with self.assertRaisesRegex(ValueError, 'label|loss'):
            audit_report(pool, plan)

    def test_pool_or_plan_tampering_fails(self):
        pool, plan = self.labeled_plan()
        changed = copy.deepcopy(plan)
        changed['proposal'][0] += 0.1
        with self.assertRaisesRegex(ValueError, 'plan|proposal'):
            audit_report(pool, changed)
        pool[0]['candidates'][0]['proxy'] = 99
        with self.assertRaisesRegex(ValueError, 'fingerprint|pool'):
            audit_report(pool, plan)

    def test_label_changes_in_source_cannot_affect_report(self):
        pool, plan = self.labeled_plan()
        before = audit_report(pool, plan)
        for p in pool:
            for c in p['candidates']:
                c['loss'] = 0
        self.assertEqual(before, audit_report(pool, plan))

    def test_duplicate_ids_and_nonfinite_numbers_rejected(self):
        for mutate in [
            lambda: self.rows[0]['candidates'][0].update(candidate_id='a'),
            lambda: self.rows[0]['candidates'][0].update(proxy=float('nan')),
        ]:
            saved = copy.deepcopy(self.rows)
            mutate()
            self.write_rows()
            with self.assertRaises(ValueError):
                load_pool(self.path)
            self.rows = saved

    def test_unrepresentable_proxy_number_is_a_validation_error(self):
        self.rows[0]['candidates'][0]['proxy'] = 10 ** 400
        self.write_rows()
        with self.assertRaises(ValueError):
            load_pool(self.path)

    def test_cli_roundtrip(self):
        plan_path = Path(self.tmp.name) / 'audit.json'
        output = Path(self.tmp.name) / 'report.json'
        completed = subprocess.run([sys.executable, '-m', 'goodhart_audit', 'plan',
            '--pool', str(self.path), '--out', str(plan_path), '--draws', '20',
            '--seed', '7', '--budgets', '1,2'], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        plan = json.loads(plan_path.read_text())
        for query in plan['queries']:
            query['loss'] = 0
        plan_path.write_text(json.dumps(plan))
        completed = subprocess.run([sys.executable, '-m', 'goodhart_audit', 'report',
            '--pool', str(self.path), '--audit', str(plan_path), '--out', str(output)],
            capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(output.read_text())['curve'])


if __name__ == '__main__':
    unittest.main()
