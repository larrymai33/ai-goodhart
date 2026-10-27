"""Failure-preservation checks for the offline reproduction entry point."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import reproduce


class ReproduceTests(unittest.TestCase):
    def test_verify_only_works_without_site_packages_and_checks_all_releases(self):
        completed = subprocess.run(
            [sys.executable, "-B", "-S", "-m", "experiments.reproduce", "--verify-only"],
            cwd=Path(__file__).resolve().parents[1], check=True,
            capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["reproduction_status"], "not_run")
        names = {check["name"] for check in report["checks"] if check["status"] == "passed"}
        self.assertTrue({"verify_published_fixed", "verify_published_anytime",
                         "verify_published_design", "verify_published_sharp_sources"} <= names)
        for check in report["checks"]:
            if "command" in check:
                self.assertIn("-S", check["command"])

    def test_existing_output_is_rejected_without_mutating_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            sentinel = out / "keep.txt"
            sentinel.write_bytes(b"original evidence")
            report = reproduce.reproduce(out)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(sentinel.read_bytes(), b"original evidence")
            self.assertEqual(list(out.iterdir()), [sentinel])

    def test_output_inside_published_results_is_rejected_before_creation(self):
        out = Path(__file__).resolve().parents[1] / "results" / "uncreated-reproduction-test"
        self.assertFalse(out.exists())
        report = reproduce.reproduce(out)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(out.exists())

    def test_comparison_reports_different_bytes_even_for_valid_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / "a.json", Path(temporary) / "b.json"
            first.write_bytes(b'{"n":1}\n')
            second.write_bytes(b'{"n": 1}\n')
            pair = reproduce.compare_artifact(first, second, "designs")
            self.assertFalse(pair["equal"])
            self.assertEqual(pair["published_sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
            self.assertEqual(pair["reproduced_sha256"], hashlib.sha256(second.read_bytes()).hexdigest())

    def test_sharp_source_changes_fail_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.py"
            source.write_bytes(b"old")
            result = root / "result.json"
            result.write_text(json.dumps({"source_sha256": {
                "source.py": hashlib.sha256(b"old").hexdigest()}}))
            with patch.object(reproduce, "SHARP_SHA256", hashlib.sha256(result.read_bytes()).hexdigest()):
                self.assertEqual(reproduce.verify_sharp(result, root)["source_count"], 1)
                source.write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "source checksum"):
                    reproduce.verify_sharp(result, root)

    def test_verify_only_rejects_numeric_only_tampering_with_intact_source_hashes(self):
        original_bytes = reproduce.SHARP.read_bytes()
        artifact = json.loads(original_bytes)
        original_sources = dict(artifact["source_sha256"])
        original_number = ('"c0_approximation": ' + json.dumps(artifact["constants"]["c0_approximation"])).encode()
        self.assertEqual(original_bytes.count(original_number), 1)
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "sharp-envelope.json"
            tampered.write_bytes(original_bytes.replace(original_number, b'"c0_approximation": 999', 1))
            self.assertEqual(json.loads(tampered.read_text())["source_sha256"], original_sources)
            with patch.object(reproduce, "SHARP", tampered):
                report = reproduce.reproduce(verify_only=True)
            self.assertEqual(report["status"], "failed")
            self.assertIn("artifact checksum", report["checks"][-1]["error"])

    def test_subprocess_failure_is_not_silently_accepted(self):
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            reproduce.run_command([sys.executable, "-c", "raise SystemExit(7)"])
        self.assertEqual(caught.exception.returncode, 7)

    def test_failed_tests_prevent_generation_and_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "fresh"
            def execute(arguments):
                if "unittest" in arguments:
                    raise subprocess.CalledProcessError(4, arguments, stderr="intentional failed test")
                if any("run_" in word for word in arguments):
                    self.fail("a generator ran after a failed test")
                return {"command": arguments, "stdout": "", "stderr": ""}
            with patch.object(reproduce, "run_command", side_effect=execute):
                report = reproduce.reproduce(out)
            self.assertEqual(report["status"], "failed")
            self.assertIn("intentional failed test", json.dumps(report))
            self.assertFalse(out.exists())

    def test_byte_mismatch_preserves_failure_report_after_generation(self):
        report = self._fake_full_run(corrupt_csv=True)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["reproduction_status"], "failed")
        failed_pairs = [pair["label"] for pair in report["checksum_pairs"] if not pair["equal"]]
        self.assertEqual(failed_pairs, ["fixed/summary.csv"])

    def test_final_comparison_rejects_identically_tampered_sharp_copies(self):
        report = self._fake_full_run(change_sharp_at_comparison=True)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["checks"][-1]["name"], "exact_artifact_comparison")
        self.assertIn("artifact checksum", report["checks"][-1]["error"])
        # Mere equality would accept this: both copies changed after validation.
        self.assertTrue(all(pair["equal"] for pair in report["checksum_pairs"]))

    def _fake_full_run(self, *, corrupt_csv=False, change_sharp_at_comparison=False):
        # The expensive generators/verifiers are replaced at their subprocess
        # boundary; real file comparisons must still reject altered evidence.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.py"
            source.write_bytes(b"source")
            sharp = root / "results/theory/sharp_envelope.json"
            sharp.parent.mkdir(parents=True)
            sharp.write_text(json.dumps({"source_sha256": {
                "source.py": hashlib.sha256(b"source").hexdigest()}, "runtime": {},
                "constants": {"c0_approximation": 1}}))
            for name, published, _, _ in reproduce.STUDIES:
                directory = root / published
                directory.mkdir(parents=True, exist_ok=True)
                filenames = ["summary.csv"] + (["designs.json"] if name == "design" else [])
                hashes = {}
                for filename in filenames:
                    (directory / filename).write_bytes(b"original\n")
                    hashes[filename] = hashlib.sha256(b"original\n").hexdigest()
                (directory / "manifest.json").write_text(json.dumps({"outputs_sha256": hashes}))
            out = root / "fresh"

            def execute(arguments):
                for name, published, _, generator in reproduce.STUDIES:
                    if generator in arguments:
                        directory = Path(arguments[arguments.index("--out") + 1])
                        directory.mkdir()
                        for filename in ["summary.csv"] + (["designs.json"] if name == "design" else []):
                            (directory / filename).write_bytes(b"changed\n" if name == "fixed" and corrupt_csv else b"original\n")
                if "experiments.check_sharp_envelope" in arguments:
                    Path(arguments[arguments.index("--out") + 1]).write_bytes(sharp.read_bytes())
                return {"command": arguments, "stdout": "", "stderr": "Ran 1 test\nOK\n"}

            real_compare = reproduce.compare_artifact
            def compare(published, regenerated, label):
                if change_sharp_at_comparison and label == "sharp-envelope.json":
                    artifact = json.loads(Path(published).read_text())
                    artifact["constants"] = {"c0_approximation": 999}
                    for path in (published, regenerated):
                        Path(path).write_text(json.dumps(artifact))
                return real_compare(published, regenerated, label)

            with patch.object(reproduce, "ROOT", root), patch.object(reproduce, "SHARP", sharp), \
                    patch.object(reproduce, "SHARP_SHA256", hashlib.sha256(sharp.read_bytes()).hexdigest()), \
                    patch.object(reproduce, "compare_artifact", side_effect=compare), \
                    patch.object(reproduce, "run_command", side_effect=execute):
                report = reproduce.reproduce(out)
            self.assertEqual(json.loads((out / "reproduction-report.json").read_text()), report)
            self.assertEqual((root / "results/summary.csv").read_bytes(), b"original\n")
            return report


if __name__ == "__main__":
    unittest.main()
