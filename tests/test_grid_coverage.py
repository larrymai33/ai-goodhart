"""Regression checks for exact grid-coverage evidence generation."""
from fractions import Fraction as F
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    check = importlib.import_module('experiments.check_grid_coverage')
except ModuleNotFoundError as error:
    if error.name != 'experiments.check_grid_coverage':
        raise
    check = None


class GridCoverageRunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, 'grid coverage checker missing')

    def test_protocol_is_canonical_and_rejects_float_version_or_duplicates(self):
        self.assertEqual(check.read_protocol(check.DEFAULT_PROTOCOL),check.PROTOCOL)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'protocol.json'
            for content in ('{"version":1,"version":1}',json.dumps(dict(check.PROTOCOL,version=1.0)),
                            json.dumps(dict(check.PROTOCOL,pascal_max_pool=1000000)),'x'*16385):
                p.write_text(content)
                with self.assertRaises(ValueError):
                    check.read_protocol(p)

    def test_binary_witness_is_actually_binary_and_breaks_unqualified_transfer(self):
        result=check.original_witnesses()
        binary=result['binary']
        self.assertEqual(binary['positive_cells'],8)
        self.assertEqual(binary['max_grid_risk'],F(3,32))
        self.assertEqual(binary['max_full_risk'],F(2159,21504))
        self.assertEqual(binary['maximizers'],[51])
        self.assertGreater(binary['max_full_risk'],F(1,10))
        self.assertEqual(result['fractional']['max_full_risk'],F(27,256))
        self.assertEqual(result['fractional']['maximizers'],[48])

    def test_existing_output_rejected_before_computation(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'result.json'
            out.write_text('keep me')
            with patch.object(check,'compute',side_effect=AssertionError('must not run')):
                with self.assertRaises(FileExistsError):
                    check.run(out)
            self.assertEqual(out.read_text(),'keep me')

    def test_source_drift_prevents_result_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'result.json'
            with patch.object(check,'source_snapshot',side_effect=[{'a':'before'},{'a':'after'}]):
                with patch.object(check,'compute',return_value={}):
                    with self.assertRaises(RuntimeError):
                        check.run(out)
            self.assertFalse(out.exists())

    def test_serialization_is_exact_deterministic_and_rejects_float(self):
        value={'a':[F(1,3),2,True], 'b':F(0)}
        self.assertEqual(check.encode(value),check.encode(value))
        self.assertEqual(json.loads(check.encode(value)),{'a':['1/3',2,True],'b':'0'})
        with self.assertRaises(TypeError):
            check.encode({'float':0.5})

    def test_source_pins_hash_the_actual_imported_helper(self):
        import hashlib
        snapshot=check.source_snapshot()
        self.assertEqual(len(snapshot),6)
        self.assertEqual(snapshot['goodhart_audit/coverage.py'],
                         hashlib.sha256(Path(check.coverage.__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    unittest.main()
