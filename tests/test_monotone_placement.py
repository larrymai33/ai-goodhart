"""Independent tests for the registered monotone-placement lower screen."""

from contextlib import redirect_stderr
from fractions import Fraction as F
import hashlib
import importlib
import io
import itertools
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_finite_decision as previous

try:
    check = importlib.import_module("experiments.check_monotone_placement")
except ModuleNotFoundError as error:
    if error.name != "experiments.check_monotone_placement":
        raise
    check = None

ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/"experiments/monotone_placement_protocol.json").read_text())


class MonotonePlacementTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, "monotone-placement checker implementation is missing")

    def test_new_integer_dp_conforms_to_frozen_program_and_preserves_old_cap(self):
        for args in ((2, 0, 1, 0), (8, 2, 1, 100), (32, 3, 2, 2048), (1024, 0, 13, 2048)):
            self.assertEqual(check.exact_dual(*args), previous.exact_dual(*args))
        row = check.exact_dual(2048, 0, 1, 4096)
        self.assertEqual(F(row["value_numerator"], row["denominator"]), 2048)
        self.assertEqual(row["null_certificate_numerator"], row["denominator"])
        with self.assertRaises(ValueError):
            previous.exact_dual(2048, 0, 1, 4096)

    def test_posterior_recurrence_independently_matches_value_and_policy_mass(self):
        from functools import lru_cache
        for size, count, added, penalty in ((8, 0, 1, 8), (12, 2, 3, 100), (16, 4, 2, 2048)):
            def choose(n, k):
                return comb(n, k) if 0 <= k <= n else 0
            @lru_cache(None)
            def visit(t, s):
                p = choose(size-t, count-s)
                if not p:
                    return F(0), F(0), F(0)
                lr = F(choose(size-t, count+added-s)*comb(size, count), p*comb(size, count+added))
                if not lr:
                    return F(0), F(0), F(0)
                u = F(count-s, size-t)
                v0, c0, e0 = visit(t+1, s)
                v1, c1, e1 = visit(t+1, s+1)
                cost = 1+(1-u)*c0+u*c1
                error = (1-u)*e0+u*e1
                value = 1+(1-u)*v0+u*v1
                return (value, cost, error) if (value, error) < (penalty*lr, lr) else (penalty*lr, F(0), lr)
            row = check.exact_dual(size, count, added, penalty)
            expected = visit(0, 0)
            self.assertEqual(tuple(F(row[key], row["denominator"]) for key in
                                   ("value_numerator", "policy_cost_numerator", "policy_error_numerator")), expected)

    def test_sorting_worst_case_matches_explicit_latent_subsets(self):
        for weights in ((5, 3, 1), (4, 4, 2, 1), (2, 1, 1, 0)):
            for assignment in itertools.product(range(3), repeat=len(weights)):
                unknown = [i for i, code in enumerate(assignment) if code == 1]
                fixed = sum(w for w, code in zip(weights, assignment) if code == 2)
                for count in range(len(unknown)+1):
                    worst = max(fixed+sum(weights[i] for i in chosen)
                                for chosen in itertools.combinations(unknown, count))
                    row = check.sorting_worst_case(weights, assignment, count)
                    self.assertEqual(row["original_worst"], worst)
                    self.assertLessEqual(row["sorted_worst"], worst)
        with self.assertRaises(ValueError):
            check.sorting_worst_case((1, 2), (0, 1), 1)

    def test_small_frontiers_match_exhaustive_heads_and_all_null_subsets(self):
        rows = ((F(1, 4),)*4, (F(2, 5), F(3, 10), F(1, 5), F(1, 10)))
        for count in (0, 1):
            total, added, threshold = 1, 1, F(1, 4)
            fixed = total-count
            feasible = []
            for head in range(4-fixed-count-added+1):
                positions = range(head, 4-fixed)
                risks = [sum(row[4-fixed:], F(0))+sum((row[i] for i in subset), F(0))
                         for row in rows for subset in itertools.combinations(positions, count)]
                if max(risks) <= threshold:
                    feasible.append(head)
            actual = check.minimal_head(rows, total, count, added, threshold)
            self.assertEqual(actual["head_zeros"], min(feasible))
        self.assertEqual(check.minimal_head(rows, 1, 1, 1, F(1, 4))["head_zeros"], 2)

    def test_actual_frontier_and_clean_witness_keep_all_original_targets(self):
        zero = check.frontier_for_count(0)
        self.assertEqual((zero["head_zeros"], zero["fixed_bottom_ones"], zero["unknown_population"]), (0, 192, 1856))
        frontier = check.frontier_for_count(80)
        self.assertEqual((frontier["head_zeros"], frontier["unknown_population"]), (286, 1650))
        self.assertTrue(frontier["predecessor_infeasible"])
        self.assertTrue(frontier["predecessor_violation_budgets"])
        self.assertEqual(list(frontier["null_worst_risks"]), ["1", "2", "4", "8", "16", "32", "64"])
        clean = check.placement_geometry(288, 80)
        self.assertEqual(clean["unknown_population"], 1648)
        self.assertTrue(clean["all_original_targets_margin_safe"])
        self.assertEqual(F(clean["alternative_uniform_excess"]), F(1, 10240))
        with self.assertRaises(ValueError):
            check.frontier_for_count(193)

    def test_latent_identity_matches_direct_subset_counts(self):
        for larger in range(1, 7):
            for smaller in range(1, larger+1):
                for positives in range(smaller+1):
                    counts = {}
                    for latent in itertools.combinations(range(larger), smaller):
                        for chosen in itertools.combinations(latent, positives):
                            counts[chosen] = counts.get(chosen, 0)+1
                    row = check.latent_subset_identity(larger, smaller, positives)
                    self.assertEqual(sum(counts.values()), row["left_count"])
                    self.assertEqual(row["left_count"], row["right_count"])
                    self.assertEqual(len(set(counts.values())), 1)

    def test_zero_error_scope_and_blind_mix_have_exact_distinct_arithmetic(self):
        row = check.zero_error_certificates()
        self.assertEqual(row["randomized_zero_error_lower"], 2034)
        self.assertEqual(row["deterministic_zero_error_exact"], 2036)
        self.assertEqual(F(row["fifteen_unseen_uniform_risk_increase"]), F(435, 65536))
        self.assertGreater(F(row["fifteen_unseen_uniform_risk_increase"]), F(1, 160))
        self.assertLessEqual(F(row["fourteen_unseen_uniform_risk_increase"]), F(1, 160))
        self.assertEqual(F(row["blind_delta_mixture_expected_upper"]), F(9671, 5))
        self.assertEqual(row["zero_error_scope_delta"], "0")
        self.assertEqual(row["blind_mixture_scope_delta"], "1/20")
        adversary = row["deterministic_adversary_geometry"]
        self.assertEqual((adversary["head_zeros"], adversary["null_unknown_ones"]), (1024, 192))
        self.assertTrue(adversary["all_original_targets_margin_safe"])
        self.assertEqual(set(adversary["null_worst_risks"]), {"1", "2", "4", "8", "16", "32", "64"})
        self.assertTrue(all(F(risk) <= F(3, 32) for risk in adversary["null_worst_risks"].values()))

    def test_rounding_and_registered_selection_do_not_claim_global_optimization(self):
        rows = [check.dual_certificate(4, 1, 1, penalty, F(1, 4), 8) for penalty in (1, 3, 10)]
        selected = check.select_registered(rows)
        self.assertEqual(F(selected["dual_lower_exact"]), max(F(row["dual_lower_exact"]) for row in rows))
        self.assertFalse(selected["globally_optimized_prior_or_multiplier"])
        self.assertEqual(check.decimal_bound(F(1, 3)), "0.333333333")
        self.assertEqual(check.decimal_bound(F(1, 3), upward=True), "0.333333334")
        for row in rows:
            self.assertGreaterEqual(row["rounded_lower_integer_residual"], 0)

    def test_protocol_freeze_rejects_expansion_types_and_duplicate_keys(self):
        for key, value in (("version", True), ("version", 1.0), ("multipliers", [8193]),
                           ("title", "changed"), ("sorting_max_items", 12)):
            altered = protocol()
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check.validate_protocol(altered)
        for raw in (b'{"version":1,"version":1}', b'{"x":NaN}', b" "*16385):
            with self.assertRaises(ValueError):
                check.parse_protocol(raw)
        self.assertEqual(check.validate_protocol(protocol()), protocol())

    def fixture(self, directory):
        root = Path(directory)
        for folder in ("experiments", "tests", "docs"):
            (root/folder).mkdir()
        for relative in ("experiments/check_monotone_placement.py", "tests/test_monotone_placement.py",
                         "experiments/monotone_placement_protocol.json", "experiments/check_finite_decision.py",
                         "experiments/check_sharp_cost.py"):
            (root/relative).write_bytes((ROOT/relative).read_bytes())
        for name in ("monotone-placement-theorem.md", "finite-decision-theorem.md"):
            (root/"docs"/name).write_text("Temporary proof fixture.\n")
        return root, root/"experiments/monotone_placement_protocol.json"

    def test_seven_pins_bounded_snapshot_and_each_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def bounded(candidate):
                if candidate == path:
                    self.fail("protocol must use a bounded stream")
                return original_read(candidate)
            with patch.object(check, "ROOT", root), \
                 patch.object(check, "__file__", str(root/"experiments/check_monotone_placement.py")), \
                 patch.object(check, "IMPORTED_DECISION_PATH", root/"experiments/check_finite_decision.py"), \
                 patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                 patch.object(check, "calculate", return_value={"fixture": True}), \
                 patch.object(Path, "read_bytes", bounded):
                row = check.build_results(None, path)
            self.assertEqual(len(row["source_sha256"]), 7)
            self.assertEqual(row["protocol_sha256"], hashlib.sha256(original_read(path)).hexdigest())
            for relative in row["source_sha256"]:
                source = root/relative
                original = source.read_bytes()
                def mutate(_protocol):
                    source.write_bytes(original+b"\n")
                    return {}
                with patch.object(check, "ROOT", root), \
                     patch.object(check, "__file__", str(root/"experiments/check_monotone_placement.py")), \
                     patch.object(check, "IMPORTED_DECISION_PATH", root/"experiments/check_finite_decision.py"), \
                     patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                     patch.object(check, "calculate", side_effect=mutate):
                    with self.subTest(source=relative), self.assertRaisesRegex(RuntimeError, "changed"):
                        check.build_results(None, path)
                source.write_bytes(original)

    def test_overwrite_and_invalid_protocol_do_not_start_work(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            root, path = self.fixture(directory)
            out = root/"result.json"
            out.write_bytes(b"preserve")
            with patch.object(check, "build_results", side_effect=AssertionError("work started")):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(out)]), 0)
            self.assertEqual(out.read_bytes(), b"preserve")
            path.write_text('{"invalid":true}')
            absent = root/"new-parent/result.json"
            self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(absent)]), 0)
            self.assertFalse(absent.parent.exists())

    def test_runtime_caps_and_optimization_do_not_disable_certificates(self):
        with patch.object(check, "MAX_INTEGER_BITS", 4):
            with self.assertRaises(RuntimeError):
                check.exact_dual(16, 3, 2, 100)
        code = ("from unittest.mock import patch\nfrom experiments import check_monotone_placement as c\n"
                "with patch.object(c, 'MAX_INTEGER_BITS', 4):\n    c.exact_dual(16,3,2,100)\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
