"""Small exact and fail-closed tests for the sparse-grid proof checker."""

from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_sparse_grid as check


ROOT = Path(__file__).resolve().parents[1]


def miniature_protocol():
    protocol = json.loads((ROOT/"experiments/sparse_grid_protocol.json").read_text())
    protocol.update(exhaustive_max_pool_size=3, prompt_counts=[1, 2],
                    cost_scales=["1/4", "8"],
                    additional_geometries=[{"prompts": 3, "pool_size": 8, "budgets": [1, 3, 8]}],
                    counterexample_j=[1, 2], counterexample_binary_enumeration_max_j=2)
    return protocol


class SparseGridTests(unittest.TestCase):
    def test_greedy_blocks_can_leave_gaps_and_retain_declared_rows(self):
        blocks = check.greedy_blocks(64, [64, 19, 7, 3, 1])
        self.assertEqual([row["budget"] for row in blocks], [1, 7, 64])
        self.assertEqual([(row["first_rank"], row["last_rank"]) for row in blocks],
                         [(17, 64), (3, 9), (1, 1)])
        ranks = [r for row in blocks for r in range(row["first_rank"], row["last_rank"]+1)]
        self.assertEqual(len(ranks), len(set(ranks)))
        self.assertLess(len(ranks), 64)

    def test_exact_cost_matches_independent_binomial_calculation(self):
        from math import comb
        for m, budgets, prompts, scale in [(1, [1], 1, F(1, 16)),
                                           (6, [1, 3, 6], 2, F(7, 3)),
                                           (12, [1, 2, 11], 8, F(64))]:
            result = check.check_geometry(m, budgets, prompts, scale)
            envelope = [max(F(comb(m-r, n-1), comb(m, n)) if m-r >= n-1 else F(0)
                            for n in budgets) for r in range(1, m+1)]
            expected = prompts*sum((min(F(1), scale*w/prompts) for w in envelope), F(0))
            self.assertEqual(F(result["envelope_cost_upper"]), expected)
            self.assertLessEqual(expected, 8*F(result["block_scale"]))
            self.assertEqual(F(result["ratio"]), expected/F(result["block_scale"]))

    def test_symbolic_counterexample_and_exhaustive_binary_supports(self):
        for j in [1, 2, 4, 320]:
            result = check.counterexample(j, enumerate_binary=j <= 4)
            self.assertEqual(result["support_size"], j+1)
            self.assertEqual(F(result["top_weight"]), F(9, 10))
            self.assertEqual(F(result["tail_weight"]), F(1, 10))
            self.assertEqual(F(result["competitive_ratio_lower"]), F((j+1)*65535, 65536))
            self.assertEqual(result["binary_support_tables_checked"], 2**(j+1) if j <= 4 else 0)
            self.assertNotIn("delta_denominator", result)
            self.assertLess(len(json.dumps(result)), 10000)

    def test_invalid_geometry_and_protocol_rejected_before_sweep(self):
        for args in [(0, [1], 1, F(1)), (3, [2], 1, F(1)), (3, [1, 1], 1, F(1)),
                     (3, [1, True], 1, F(1)), (3, [1, 4], 1, F(1)),
                     (3, [1], True, F(1)), (3, [1], 1, F(0)), (3, [1], 1, 0.5)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                check.check_geometry(*args)
        base = miniature_protocol()
        variants = []
        for key, value in [("exhaustive_max_pool_size", 13), ("prompt_counts", [1, True]),
                           ("cost_scales", ["0"]), ("counterexample_j", [321]),
                           ("counterexample_binary_enumeration_max_j", 5), ("additional_geometries", [])]:
            changed = deepcopy(base)
            changed[key] = value
            variants.append(changed)
        for key, value in [("factor", 1), ("maximum_risk_threshold", "1/4"), ("envelope_cost_factor", 8.0)]:
            changed = deepcopy(base)
            changed["theorem"][key] = value
            variants.append(changed)
        changed = deepcopy(base)
        del changed["theorem"]
        variants.append(changed)
        for protocol in variants:
            with self.subTest(protocol=protocol), self.assertRaises(ValueError):
                check.validate_protocol(protocol)

    def test_noncanonical_scale_grammar_is_rejected_before_fraction_construction(self):
        for text in ["1e10000000000", "1e-10000000000", "0.5", "1/0", "01", "1/02", "-1"]:
            protocol = miniature_protocol()
            protocol["cost_scales"] = [text]
            with self.subTest(text=text), patch.object(check, "F", side_effect=AssertionError("fraction conversion reached")) as fraction:
                with self.assertRaises(ValueError):
                    check.validate_protocol(protocol)
                fraction.assert_not_called()

    def fixture(self, directory, protocol=None):
        root = Path(directory)
        (root/"tests").mkdir()
        (root/"docs").mkdir()
        (root/"tests/test_sparse_grid.py").write_bytes(Path(__file__).read_bytes())
        (root/"docs/sparse-grid-theorem.md").write_text("Temporary proof fixture for a bounded unit test.\n")
        path = root/"protocol.json"
        path.write_text(json.dumps(protocol or miniature_protocol()))
        return root, path

    def test_miniature_run_counts_exact_maximum_and_pins_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            protocol = miniature_protocol()
            with patch.object(check, "ROOT", root):
                result = check.build_results(protocol, path)
                repeated = check.build_results(protocol, path)
            self.assertEqual(result, repeated)
            self.assertEqual(result["checks"]["exhaustive_families"], 7)
            self.assertEqual(result["checks"]["geometry_cases"], 15)
            self.assertEqual(result["checks"]["cost_scale_checks"], 30)
            maximum = result["checks"]["maximum_observed_ratio"]
            witness = maximum["witness"]
            self.assertEqual(F(maximum["value"]), F(check.check_geometry(
                witness["pool_size"], witness["budgets"], witness["prompts"],
                F(witness["cost_scale"]))["ratio"]))
            self.assertEqual(result["source_sha256"]["protocol.json"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(len(result["source_sha256"]), 4)

    def test_protocol_snapshot_mutation_and_supplied_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            protocol = miniature_protocol()
            original_read = Path.read_bytes
            mutated = False
            def read_then_mutate(candidate):
                nonlocal mutated
                data = original_read(candidate)
                if candidate.resolve() == path.resolve() and not mutated:
                    mutated = True
                    path.write_bytes(data+b"\n")
                return data
            with patch.object(check, "ROOT", root), patch.object(Path, "read_bytes", read_then_mutate):
                with self.assertRaisesRegex(RuntimeError, "changed"):
                    check.build_results(protocol, path)
            changed = deepcopy(protocol)
            changed["cost_scales"] = ["1"]
            with patch.object(check, "ROOT", root), self.assertRaises(ValueError):
                check.build_results(changed, path)

    def test_cli_preserves_existing_output_and_writes_nothing_on_invalid_protocol(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            output = root/"result.json"
            output.write_bytes(b"existing evidence")
            with patch.object(check, "ROOT", root), patch.object(check, "build_results", side_effect=AssertionError("work started")):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(output)]), 0)
            self.assertEqual(output.read_bytes(), b"existing evidence")
            bad = miniature_protocol()
            bad["theorem"]["factor"] = 999
            path.write_text(json.dumps(bad))
            destination = root/"new-parent/result.json"
            with patch.object(check, "ROOT", root):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(destination)]), 0)
            self.assertFalse(destination.parent.exists())

    def test_correctness_failure_remains_active_under_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_sparse_grid as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.check_geometry(4,[1],1,F(1))\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
