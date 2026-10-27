"""Small deterministic checks of the frozen cached-auditor demonstration."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
import importlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    runner = importlib.import_module("experiments.run_cached_reference")
except ModuleNotFoundError as error:
    if error.name != "experiments.run_cached_reference":
        raise
    runner = None

ROOT = Path(__file__).resolve().parents[1]


class CachedReferenceRunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(runner, "cached reference runner is not implemented")

    def small_protocol(self):
        protocol = deepcopy(runner.CANONICAL_PROTOCOL)
        protocol["prompts"] = [1]
        protocol["pool_size"] = 3
        protocol["budgets"] = [1, 2, 3]
        protocol["seeds"] = [11]
        protocol["registered_runs"] = 5
        return protocol

    def fixture(self, directory):
        root = Path(directory)
        files = (
            "experiments/run_cached_reference.py",
            "experiments/cached_reference_protocol.json",
            "tests/test_cached.py", "tests/test_cached_math.py",
            "tests/test_cached_exact.py", "tests/test_cached_reference_runner.py",
            "docs/cached-reference-numerics.md", "docs/cached-likelihood-audit.md",
        )
        for relative in files:
            target = root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/relative).read_bytes())
        engine = root/"loaded/actual_engine.py"
        math = root/"loaded/actual_math.py"
        engine.parent.mkdir()
        engine.write_bytes((ROOT/"goodhart_audit/cached.py").read_bytes())
        math.write_bytes((ROOT/"goodhart_audit/cached_math.py").read_bytes())
        return root, engine, math

    def fixture_patches(self, root, engine, math):
        return patch.multiple(runner, ROOT=root,
                              __file__=str(root/"experiments/run_cached_reference.py"),
                              IMPORTED_ENGINE_PATH=engine, IMPORTED_MATH_PATH=math)

    def test_canonical_protocol_is_fixed_bounded_and_type_sensitive(self):
        data = (ROOT/"experiments/cached_reference_protocol.json").read_bytes()
        parsed = runner.parse_protocol(data)
        self.assertEqual(runner.validate_protocol(parsed), parsed)
        self.assertEqual(parsed["registered_runs"], 45)
        self.assertEqual(parsed["source_pin_count"], 10)
        for key, value in (("version", True), ("version", 1.0),
                           ("seeds", [11]), ("registered_runs", 46),
                           ("prompts", [1, 32, 1025])):
            changed = deepcopy(parsed)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.validate_protocol(changed)
        for bad in (b'{"version":1,"version":1}', b'{"x":NaN}',
                    b'{"x":Infinity}', b" "*16385):
            with self.subTest(bad=bad[:30]), self.assertRaises(ValueError):
                runner.parse_protocol(bad)

    def test_small_matrix_schema_truth_scope_and_completion(self):
        protocol = self.small_protocol()
        with patch.object(runner, "CANONICAL_PROTOCOL", protocol):
            result = runner.calculate(protocol)
        self.assertEqual(result["run_count"], 5)
        rows = {row["scenario"]: row for row in result["runs"]}
        self.assertEqual(tuple(rows), ("all_zero", "constant_margin", "rare_top",
                                      "boundary_constant", "unsafe_constant"))
        self.assertEqual(rows["rare_top"]["exact_truth_risks"],
                         {"1": "1/32", "2": "1/16", "3": "3/32"})
        for name, row in rows.items():
            self.assertEqual(row["mode"], "prefix")
            self.assertEqual(row["proposals"], 0)
            self.assertEqual((row["distinct_labels"], row["oracle_calls"]), (3, 3))
            self.assertEqual(row["phase_counts"], {"proposal": 0, "prefix": 3, "census": 0})
            self.assertEqual(row["expected_label_bound"], "3")
            self.assertRegex(row["acquisition_trace_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotIn("acquisitions", row)
            self.assertNotIn("runtime", row)
            self.assertEqual(row["whole_family_safe"], name != "unsafe_constant")
            self.assertEqual(row["margin_safe"], name not in ("boundary_constant", "unsafe_constant"))
            self.assertEqual(row["status"], "not_certified" if name == "unsafe_constant" else "certified")

    def test_trace_digest_has_independent_canonical_record_encoding(self):
        protocol = self.small_protocol()
        row = runner.run_case(protocol, 1, "all_zero", 11)
        digest = hashlib.sha256()
        for rank in range(3):
            record = {"prompt_index": 0, "rank_index": rank, "loss": "0",
                      "phase": "prefix", "budget": None, "proposal_index": None}
            digest.update((json.dumps(record, sort_keys=True, separators=(",", ":"))+
                           "\n").encode("utf-8"))
        self.assertEqual(row["acquisition_trace_sha256"], digest.hexdigest())

    def test_seeded_real_likelihood_case_is_reproducible(self):
        protocol = self.small_protocol()
        protocol.update(pool_size=1, budgets=[1], tau="3/4", epsilon="1/2",
                        delta="1/4", eta="1/10")
        first = runner.run_case(protocol, 8, "all_zero", 11)
        second = runner.run_case(protocol, 8, "all_zero", 11)
        self.assertEqual(first, second)
        self.assertEqual(first["mode"], "likelihood")
        self.assertEqual(first["proposals"], 2)
        self.assertEqual(first["budget_results"][0]["pass_reason"], "likelihood")

    def test_duplicate_oracle_calls_are_detected(self):
        def broken_audit(*args, **kwargs):
            oracle = args[6]
            oracle(0, 0)
            oracle(0, 0)
        with patch.object(runner.cached, "audit", side_effect=broken_audit):
            with self.assertRaisesRegex(RuntimeError, "once"):
                runner.run_case(self.small_protocol(), 1, "all_zero", 11)

    def test_trace_mismatch_and_safe_noncompletion_are_detected(self):
        real = runner.cached.audit
        for defect in ("trace", "completion"):
            def broken_audit(*args, **kwargs):
                result = real(*args, **kwargs)
                return (replace(result, acquisitions=result.acquisitions[:-1])
                        if defect == "trace" else replace(result, status="not_certified"))
            with self.subTest(defect=defect), patch.object(runner.cached, "audit", side_effect=broken_audit):
                with self.assertRaises(RuntimeError):
                    runner.run_case(self.small_protocol(), 1, "all_zero", 11)

    def test_unsafe_statistical_pass_is_recorded_without_zero_error_claim(self):
        # A partial trace need not expose an unsafe table's full risk. This
        # result double tests reporting, not the real engine's probability.
        def statistical_pass(*args, **kwargs):
            plan = runner.cached.design(*args[:6], eta=kwargs["eta"])
            loss = Fraction(args[6](0, 0))
            rows = tuple(runner.cached.BudgetResult(n, "passed", "likelihood", 0, 0, None)
                         for n in plan.budgets)
            trace = (runner.cached.Acquisition(0, 0, loss, "prefix", None, None),)
            return runner.cached.AuditResult("certified", plan, trace, rows, None, None)
        with patch.object(runner.cached, "audit", side_effect=statistical_pass):
            row = runner.run_case(self.small_protocol(), 2, "unsafe_constant", 11)
        self.assertFalse(row["whole_family_safe"])
        self.assertTrue(row["false_certificate"])

    def test_certificate_contradicting_observed_risk_is_rejected(self):
        real = runner.cached.audit
        def contradictory(*args, **kwargs):
            return replace(real(*args, **kwargs), status="certified")
        with patch.object(runner.cached, "audit", side_effect=contradictory):
            with self.assertRaisesRegex(RuntimeError, "observed"):
                runner.run_case(self.small_protocol(), 1, "unsafe_constant", 11)

    def test_actual_imported_paths_are_used(self):
        self.assertEqual(runner.IMPORTED_ENGINE_PATH, Path(runner.cached.__file__).resolve())
        math_module = importlib.import_module(runner.cached.design.__module__)
        self.assertEqual(runner.IMPORTED_MATH_PATH, Path(math_module.__file__).resolve())

    def test_ten_pins_bounded_protocol_snapshot_and_each_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root, engine, math = self.fixture(directory)
            protocol_path = root/"experiments/cached_reference_protocol.json"
            original_read = Path.read_bytes
            def bounded(path):
                if path == protocol_path:
                    self.fail("protocol snapshot must use bounded reads")
                return original_read(path)
            with self.fixture_patches(root, engine, math), \
                 patch.object(runner, "calculate", return_value={"run_count": 0, "runs": []}), \
                 patch.object(Path, "read_bytes", bounded):
                result = runner.build_results()
            pins = result["source_sha256"]
            self.assertEqual(len(pins), 10)
            self.assertIn("loaded/actual_engine.py", pins)
            self.assertIn("loaded/actual_math.py", pins)
            self.assertNotIn("goodhart_audit/cached.py", pins)
            self.assertEqual(result["protocol_sha256"], hashlib.sha256(original_read(protocol_path)).hexdigest())
            for relative in pins:
                path = root/relative
                original = path.read_bytes()
                def mutate(_protocol):
                    path.write_bytes(original+b"\n")
                    return {"run_count": 0, "runs": []}
                with self.subTest(source=relative), self.fixture_patches(root, engine, math), \
                     patch.object(runner, "calculate", side_effect=mutate):
                    with self.assertRaisesRegex(RuntimeError, "changed"):
                        runner.build_results()
                path.write_bytes(original)

    def test_overwrite_and_invalid_protocol_do_not_start_calculation(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            root, engine, math = self.fixture(directory)
            out = root/"old.json"
            out.write_bytes(b"preserve")
            with patch.object(runner, "build_results", side_effect=AssertionError("work started")):
                self.assertEqual(runner.main(["--out", str(out)]), 2)
            self.assertEqual(out.read_bytes(), b"preserve")
            (root/"experiments/cached_reference_protocol.json").write_text('{"invalid":true}')
            absent = root/"new-parent/result.json"
            with self.fixture_patches(root, engine, math), \
                 patch.object(runner, "calculate", side_effect=AssertionError("work started")):
                self.assertEqual(runner.main(["--out", str(absent)]), 2)
            self.assertFalse(absent.parent.exists())

    def test_exclusive_output_create_prevents_race_overwrite(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            out = Path(directory)/"raced.json"
            def race():
                out.write_bytes(b"preserve-race")
                return {"fixture": True}
            with patch.object(runner, "build_results", side_effect=race):
                self.assertEqual(runner.main(["--out", str(out)]), 2)
            self.assertEqual(out.read_bytes(), b"preserve-race")

    def test_cli_has_no_protocol_override(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            runner.main(["--protocol", "other.json", "--out", "unused.json"])


if __name__ == "__main__":
    unittest.main()
