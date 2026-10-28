"""Artifact guards and independently computable finite-chain cases."""
from contextlib import redirect_stderr
from fractions import Fraction as F
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_repeated_screening as check


class ScreeningCheckerTests(unittest.TestCase):
    def test_one_state_absorbing_chain_matches_geometric_wait(self):
        self.assertEqual(check.absorbing_solution(F(3,16), F(3,16), 1, True), F(1,2))
        self.assertEqual(check.absorbing_solution(F(3,16), F(3,16), 1, False), F(8,3))
        self.assertEqual(check.absorbing_solution(F(1,2), F(1,4), 0, True), 1)
        self.assertEqual(check.absorbing_solution(F(1,2), F(1,4), 0, False), 0)

    def test_full_gate_grid_checks_sharper_cost_and_corrected_law(self):
        self.assertEqual(check.gate_checks(), 561)

    def test_existing_output_is_preserved_before_any_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'result.json'
            target.write_text('existing', encoding='utf-8')
            with patch.object(check, 'build_document', side_effect=AssertionError('must not calculate')):
                with redirect_stderr(io.StringIO()):
                    self.assertEqual(check.main(['--out', str(target)]), 2)
            self.assertEqual(target.read_text(), 'existing')

    def test_protocol_rejects_duplicate_keys_extra_fields_and_type_changes(self):
        canonical = json.loads(check.PROTOCOL.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'protocol.json'
            changed = dict(canonical, version=True)
            for text in [json.dumps(changed), json.dumps(dict(canonical, extra=1)),
                         '{"version":1,"version":1}',
                         json.dumps(canonical).replace('13000', '13000.0')]:
                path.write_text(text, encoding='utf-8')
                with self.subTest(text=text[:40]), self.assertRaises(ValueError):
                    check.load_protocol(path)

    def test_source_drift_aborts_without_certificate(self):
        with patch.object(check, 'source_pins', side_effect=[{'source': 'before'}, {'source': 'after'}]):
            with self.assertRaisesRegex(ValueError, 'changed'):
                check.build_document()

    def test_current_source_pins_and_repeated_builds_match(self):
        first = check.build_document()
        self.assertEqual(first, check.build_document())
        self.assertEqual(first['source_sha256'], check.source_pins())
        self.assertEqual(first['gate_cases'], 561)
        self.assertEqual(len(first['illustrative_traces']), 5)
        self.assertEqual(len(first['examples']), 2)


if __name__ == '__main__':
    unittest.main()
