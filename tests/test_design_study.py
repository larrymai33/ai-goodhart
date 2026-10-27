import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    import numpy
    import scipy
except ImportError as exc:
    raise unittest.SkipTest('optional design study requires existing NumPy/SciPy') from exc

from experiments.run_anytime_study import run as run_base
from experiments.run_design_study import run
from experiments.verify_design_results import verify


class DesignStudyTests(unittest.TestCase):
    def make_base(self, folder):
        base = json.loads(Path('experiments/anytime_protocol.json').read_text())
        base.update(pool_size=16, budgets=[1, 2, 4, 8, 16],
                    label_checkpoints=[2], max_labels=2, replicates=2,
                    scenarios=['all_safe'], methods=['uniform'])
        protocol = folder / 'base-protocol.json'
        protocol.write_text(json.dumps(base))
        results = folder / 'base'
        run_base(base, results, draw_plots=False)
        followup = json.loads(Path('experiments/design_protocol.json').read_text())
        followup.update(base_protocol=str(protocol), base_results=str(results),
                        new_methods=['variance_optimal'],
                        base_manifest_sha256=hashlib.sha256((results / 'manifest.json').read_bytes()).hexdigest())
        return followup, results

    def test_reused_rows_are_identical_and_new_design_is_certified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, base = self.make_base(root)
            run(protocol, root / 'new')
            self.assertEqual(verify(root / 'new'), (4, 4, 2))
            with (base / 'replicates.csv').open(newline='') as stream:
                original = list(csv.DictReader(stream))
            with (root / 'new' / 'replicates.csv').open(newline='') as stream:
                combined = list(csv.DictReader(stream))
            self.assertEqual([r for r in combined if r['method'] == 'uniform'], original)
            designs = json.loads((root / 'new' / 'designs.json').read_text())
            self.assertLessEqual(designs['variance_optimal']['relative_gap'], 1e-5)

    def test_tampered_base_is_rejected_before_measurement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, base = self.make_base(root)
            with (base / 'replicates.csv').open('a') as stream:
                stream.write('tampered\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                run(protocol, root / 'new')
            self.assertFalse((root / 'new' / 'manifest.json').exists())

    def test_output_cannot_overwrite_frozen_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, base = self.make_base(root)
            original = {p.name: p.read_bytes() for p in base.iterdir() if p.is_file()}
            with self.assertRaisesRegex(ValueError, 'new or empty'):
                run(protocol, base)
            self.assertEqual({p.name: p.read_bytes() for p in base.iterdir() if p.is_file()}, original)

    def test_regenerated_manifest_cannot_claim_original_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, base = self.make_base(root)
            protocol['base_manifest_sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'release pin'):
                run(protocol, root / 'new')


if __name__ == '__main__':
    unittest.main()
