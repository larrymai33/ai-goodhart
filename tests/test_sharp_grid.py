"""Small exact, symbolic-resource, and provenance checks for arbitrary grids."""

from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_sharp_grid as check


ROOT = Path(__file__).resolve().parents[1]


def miniature_protocol():
    protocol = json.loads((ROOT/"experiments/sharp_grid_protocol.json").read_text())
    protocol.update(tail_max_pool_size=3, tail_epsilons=["1/4"], grid_max_pool_size=3,
                    grid_k=[4], certificate_geometries=[{"pool_size": 4, "budgets": [2, 4]}],
                    certificate_k=[8], certificate_deltas=["1/4"], counterexample_k=[2])
    return protocol


class SharpGridTests(unittest.TestCase):
    def test_tail_identity_counts_and_strict_small_weight_tail(self):
        result = check.tail_checks(3, [F(1, 4)])
        self.assertEqual(result["tail_identity_checks"], 14)
        self.assertEqual(result["empty_tail_checks"], 6)
        self.assertEqual(result["small_weight_tail_checks"], 6)
        for m in range(1, 9):
            for n in range(1, m+1):
                row = check.exact_weights(m, n)
                for r in range(1, m+1):
                    self.assertEqual(sum(row[r-1:], F()), F(m-r+1, n)*row[r-1])

    def test_missing_baseline_singleton_and_zero_support_are_preserved(self):
        result = check.grid_structure(8, [8], 4)
        self.assertEqual(result["budgets"], [8])
        self.assertEqual(result["representatives"], [8])
        self.assertEqual(result["positive_support_size"], 1)
        self.assertEqual([(b["first_rank"], b["last_rank"]) for b in result["bins"]], [(1, 1)])
        other = check.grid_structure(8, [2], 8)
        self.assertEqual(other["positive_support_size"], 7)
        self.assertEqual(other["bins"][-1]["last_rank"], 7)
        uniform = check.grid_structure(8, [1], 8)
        self.assertEqual(len(uniform["bins"]), 1)
        self.assertEqual(uniform["bins"][0]["last_rank"], 8)

    def test_skeleton_charges_windows_and_retained_mass_match_independent_sums(self):
        m, budgets, k = 10, [2, 3, 9, 10], 8
        result = check.grid_structure(m, budgets, k)
        self.assertEqual(result["representatives"], [2, 9])
        rows = {n: check.exact_weights(m, n) for n in budgets}
        envelope = [max(row[r] for row in rows.values()) for r in range(m)]
        eps, eta, tau = F(1, k), F(1, k), F(1, k**3)
        bad_mass = sum((e for e in envelope if not any(eps*n/m <= e <= F(4*n, m)
                                                     for n in result["representatives"])), F())
        self.assertEqual(F(result["bad_envelope_mass"]), bad_mass)
        self.assertLessEqual(bad_mass, 16*eps*F(result["envelope_normalizer"]))
        retained = sum((F(b["minimum_mass"]) for b in result["bins"] if F(b["minimum_mass"]) >= k*tau), F())
        self.assertEqual(F(result["retained_minimum_mass"]), retained)
        for window in result["window_bin_counts"]:
            if window["count"]:
                self.assertLessEqual((1+eta)**(window["count"]-1), 4*(1+eta)/eps)
        for b in result["bins"]:
            self.assertIn(b["witness_budget"], budgets)
        total = sum((F(b["minimum_mass"]) for b in result["bins"]), F())
        self.assertEqual(total, retained+F(result["dropped_good_bin_mass"])+F(result["dropped_bad_bin_mass"]))

    def test_tiny_generic_counterexample_reduction_for_all_binary_tables(self):
        fixture = check.tiny_counter_rows(2, 2, F(1, 4), F(1, 2))
        self.assertEqual(fixture["items"], 10)
        self.assertEqual(fixture["head_threshold"], F(1, 3))
        for row in fixture["family_rows"]:
            self.assertEqual(sum(row, F()), 1)
            self.assertTrue(all(a >= b >= 0 for a, b in zip(row, row[1:])))
        fixtures = list(product([F(0), F(1)], repeat=10))
        fixtures += [tuple([F(1, 3)]*10), tuple([F(7, 10)]*2+[F(1, 5)]*8),
                     tuple([F(0)]*2+[F(3, 4)]*8), tuple([F(1, 3)]*2+[F(1)]*8)]
        seen_head_only = seen_uniform_only = False
        for y in fixtures:
            unsafe = any(sum((a*v for a, v in zip(row, y)), F()) > fixture["risk_threshold"]
                         for row in fixture["family_rows"])
            head_bad = sum((a*v for a, v in zip(fixture["head_target"], y)), F()) > fixture["head_threshold"]
            uniform_bad = sum((a*v for a, v in zip(fixture["uniform_target"], y)), F()) > fixture["risk_threshold"]
            self.assertTrue(not unsafe or head_bad or uniform_bad)
            seen_head_only |= unsafe and head_bad and not uniform_bad
            seen_uniform_only |= unsafe and uniform_bad and not head_bad
        self.assertTrue(seen_head_only and seen_uniform_only)

    def test_symbolic_counterexample_never_expands_exponential_dimension(self):
        result = check.counterexample_certificate(64)
        self.assertEqual(result["head_size"], 64**3)
        self.assertEqual(result["tail_levels"], 64**3)
        self.assertEqual(result["population_symbolic"], "H*(1+2^J)")
        self.assertNotIn("items", result)
        lo, hi = check.log_interval(F(1, 4))
        bound = (1-hi/F(2*64**2))*64*(1+F(64, 2))/(2*64+1)
        self.assertEqual(F(result["ratio_lower"]), check.round_down(bound))
        self.assertLessEqual(F(result["display"]["ratio_lower"]), F(result["ratio_lower"]))
        self.assertLess(len(json.dumps(result)), 10000)
        with self.assertRaises(ValueError):
            check.tiny_counter_rows(64**3, 64**3, F(1, 4), F(1, 2))

    def test_arbitrary_grid_cost_certificate_is_conservative_and_symbolic(self):
        m, budgets, k, delta = 16, [3, 9, 16], 8, F(1, 20)
        result = check.cost_certificate(m, budgets, k, delta)
        self.assertEqual(result["budgets"], budgets)
        structure = check.grid_structure(m, budgets, k)
        p, tau = result["prompts"], F(result["tau"])
        lo, hi = check.log_interval(delta)
        rounded, unrounded = F(), F()
        for b in structure["bins"]:
            if b["retained"]:
                count = b["last_rank"]-b["first_rank"]+1
                v = F(b["endpoint_envelope"])/p
                bad_size = tau//v+1
                bound = check.finite_lower_bound(p*count, bad_size, lo)
                unrounded += bound
                rounded += check.round_down(bound)
        self.assertEqual(F(result["lower_bound"]), rounded)
        self.assertLess(rounded, check.round_down(unrounded))
        self.assertEqual(F(result["upper_bound"]), check.round_up(hi*F(structure["envelope_normalizer"])/tau))
        self.assertLessEqual(F(result["display"]["lower_bound"]), F(result["lower_bound"]))
        for field in ["upper_bound", "ratio_upper"]:
            self.assertGreaterEqual(F(result["display"][field]), F(result[field]))
        big = check.cost_certificate(128, [128], 512, F(1, 20))
        self.assertGreater(big["items"], 10**12)
        self.assertEqual(big["positive_support_size"], 1)
        self.assertEqual(big["budgets"], [128])

    def test_protocol_metadata_work_limits_and_fraction_grammar_fail_closed(self):
        base = miniature_protocol()
        variants = []
        for key, value in [("tail_max_pool_size", 65), ("grid_max_pool_size", 11),
                           ("grid_k", [True]), ("certificate_k", [513]), ("counterexample_k", [65]),
                           ("dyadic_rounding_bits", 80.0), ("counterexample_delta", "1/20")]:
            changed = deepcopy(base)
            changed[key] = value
            variants.append(changed)
        changed = deepcopy(base)
        changed["theorem"]["budget_family"] = "all monotone families"
        variants.append(changed)
        for protocol in variants:
            with self.assertRaises(ValueError):
                check.validate_protocol(protocol)
        for text in ["1e10000000000", "1e-10000000000", "0.25", "1/0", "01", "1/02", "-1"]:
            changed = deepcopy(base)
            changed["tail_epsilons"] = [text]
            with patch.object(check, "F", side_effect=AssertionError("Fraction called")) as fraction:
                with self.assertRaises(ValueError):
                    check.validate_protocol(changed)
                fraction.assert_not_called()
        for budgets in [[], [True], [0], [1, 1], [9]]:
            with self.assertRaises(ValueError):
                check.grid_structure(8, budgets, 4)

    def fixture(self, directory):
        root = Path(directory)
        (root/"tests").mkdir()
        (root/"docs").mkdir()
        (root/"tests/test_sharp_grid.py").write_bytes(Path(__file__).read_bytes())
        for name in ["sharp-grid-structure.md", "sharp-cost-theorem.md", "sparse-grid-theorem.md"]:
            (root/"docs"/name).write_text("Temporary source-pin fixture.\n")
        path = root/"protocol.json"
        path.write_text(json.dumps(miniature_protocol()))
        return root, path

    def test_miniature_counts_and_seven_pins_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            with patch.object(check, "ROOT", root):
                result = check.build_results(miniature_protocol(), path)
                repeated = check.build_results(miniature_protocol(), path)
            self.assertEqual(result, repeated)
            self.assertEqual(result["tail_checks"]["tail_identity_checks"], 14)
            self.assertEqual(result["grid_checks"]["grids"], 11)
            self.assertEqual(result["grid_checks"]["grid_scale_cases"], 11)
            self.assertEqual(len(result["cost_certificates"]), 1)
            self.assertEqual(len(result["monotone_counterexamples"]), 1)
            self.assertEqual(len(result["source_sha256"]), 7)
            self.assertEqual(result["source_sha256"]["protocol.json"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_snapshot_mutation_duplicate_keys_and_failed_output_preserve_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original = Path.read_bytes
            changed = False
            def read_then_change(candidate):
                nonlocal changed
                data = original(candidate)
                if candidate.resolve() == path.resolve() and not changed:
                    changed = True
                    path.write_bytes(data+b"\n")
                return data
            with patch.object(check, "ROOT", root), patch.object(Path, "read_bytes", read_then_change):
                with self.assertRaisesRegex(RuntimeError, "changed"):
                    check.build_results(miniature_protocol(), path)
            path.write_text('{"version":1,"version":1}')
            with patch.object(check, "ROOT", root), self.assertRaisesRegex(ValueError, "duplicate"):
                check.build_results(None, path)
            output = root/"result.json"
            output.write_bytes(b"preserve")
            with patch.object(check, "ROOT", root), patch.object(check, "build_results", side_effect=AssertionError("work started")):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(output)]), 0)
            self.assertEqual(output.read_bytes(), b"preserve")
            destination = root/"new-parent/result.json"
            with patch.object(check, "ROOT", root):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(destination)]), 0)
            self.assertFalse(destination.parent.exists())

    def test_checks_remain_active_under_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_sharp_grid as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.grid_structure(4,[4],4)\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
