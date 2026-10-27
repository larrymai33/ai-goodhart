"""Independent arithmetic and provenance checks for finite saturation."""

from contextlib import redirect_stderr
from decimal import Decimal, localcontext
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

try:
    check = importlib.import_module("experiments.check_finite_saturation")
except ModuleNotFoundError as error:
    if error.name != "experiments.check_finite_saturation":
        raise
    check = None

ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/"experiments/finite_saturation_protocol.json").read_text())


class FiniteSaturationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, "finite-saturation checker implementation is missing")

    def test_reciprocal_matches_independent_uniform_subsets(self):
        for size in range(2, 10):
            for ones in range(size//2+1):
                subsets = tuple(itertools.combinations(range(size), ones))
                for queried in range(size//4+1):
                    expected = sum((F(1, ones-sum(i < queried for i in subset)+1)
                                    for subset in subsets), F(0))/len(subsets)
                    actual = check.reciprocal_expectation(size, ones, queried)
                    self.assertEqual(actual, expected)
                    self.assertLessEqual(actual, F(size+1, (ones+1)*(size+1-queried)))
        self.assertEqual(check.reciprocal_expectation(8, 0, 2), 1)

    def test_conditional_majorant_bounds_independent_decimal_kl(self):
        for size, ones, added, queried, seen in ((8, 0, 1, 2, 0), (16, 4, 2, 4, 0),
                                                (16, 4, 2, 4, 4), (32, 8, 8, 8, 3)):
            row = check.conditional_majorant(size, ones, added, queried, seen)
            u, v = F(row["null_probability"]), F(row["alternative_probability"])
            self.assertEqual(u, F(ones-seen, size-queried))
            self.assertEqual(v, F(ones+added-seen, size-queried))
            with localcontext() as context:
                context.prec = 80
                ud, vd = (Decimal(x.numerator)/Decimal(x.denominator) for x in (u, v))
                kl = (ud*(ud/vd).ln() if ud else Decimal(0))
                kl += (1-ud)*((1-ud)/(1-vd)).ln()
                bound = F(row["bernoulli_kl_majorant"])
                self.assertLessEqual(kl, Decimal(bound.numerator)/Decimal(bound.denominator))
            self.assertLessEqual(F(row["bernoulli_kl_majorant"]), F(row["reciprocal_majorant"]))
        for args in ((8, 2, 3, 1, 0), (8, 1, 1, 2, 2), (8, 0, 1, 3, 0)):
            with self.assertRaises(ValueError):
                check.conditional_majorant(*args)

    def test_slice_caps_cover_zero_successes_and_large_population(self):
        small = check.slice_certificate(16, 0, 1, F(1, 4))
        self.assertEqual(small["branch"], "zero-query argument")
        self.assertEqual(F(small["rate_lower"]), 16)
        large = check.slice_certificate(4096, 128, 1, F(1, 4))
        self.assertEqual((large["cap_lower"], large["cap_upper"]), (32, 32))
        self.assertEqual(large["floor_status"], "resolved")
        self.assertLess(F(large["transcript_kl_upper"]), F(large["binary_information_lower"]))
        middle = check.slice_certificate(4096, 128, 32, F(1, 4))
        self.assertEqual(middle["branch"], "finite transcript cap")
        self.assertEqual(middle["cap_lower"], 5)
        self.assertEqual(check.floor_interval(F(25599, 100), F(25601, 100), 128),
                         (1, 2, "explicit_interval"))

    def test_dense_weights_and_clipping_match_independent_subset_enumeration(self):
        for size, budgets in ((1, [1]), (4, [1, 4]), (6, [2, 3, 6]), (8, [2, 8])):
            rows = []
            for budget in budgets:
                subsets = tuple(itertools.combinations(range(size), budget))
                rows.append(tuple(F(sum(min(s) == r for s in subsets), len(subsets))
                                  for r in range(size)))
            envelope = tuple(max(row[r] for row in rows) for r in range(size))
            case = check.dense_grid_case(32, size, budgets, F(1, 8), F(1, 128), F(1, 4))
            self.assertEqual(tuple(map(F, case["envelope"])), envelope)
            h = F(case["H_lower"])
            independent = min(F(32*k)+h*sum(envelope[k:], F(0)) for k in range(size+1))
            self.assertEqual(F(case["clipped_lower"]), independent)
            self.assertLessEqual(F(case["F_upper"]), 40*F(case["A16_lower"]))
        edge = check.dense_grid_case(1, 8, [2], F(1, 8), F(1, 128), F(1, 4))
        self.assertEqual(F(edge["maximum_adjacent_weight_ratio"]), F(6, 7))

    def test_unresolved_slice_floor_is_retained_with_outward_information_budget(self):
        original = check.log_interval
        def widened(delta):
            lo, hi = original(delta)
            return (lo-F(2, 5), hi+F(2, 5)) if delta == F(1, 20) else (lo, hi)
        with patch.object(check, "log_interval", side_effect=widened):
            row = check.slice_certificate(4096, 2, 8, F(1, 20))
        self.assertEqual((row["cap_lower"], row["cap_upper"]), (3, 5))
        self.assertEqual(row["floor_status"], "explicit_interval")
        self.assertLess(F(row["transcript_kl_upper"]), F(row["binary_information_lower"]))

    def test_fractional_prior_count_and_small_population_boundary(self):
        row = check.rank_prior_case(32, F(1, 8), F(1, 128), F(1, 4), F(1, 4))
        self.assertEqual(row["branch"], "fixed-count fractional prior")
        self.assertEqual((row["null_count"], row["added_count"]), (4, 3))
        self.assertEqual(F(row["amplitude"]), F(15, 16))
        self.assertEqual(F(row["null_rank_average"]), F(15, 128))
        self.assertGreaterEqual(F(row["risk_increase"]), F(1, 64))
        for prompts, tau, eps, expected in ((31, F(1, 8), F(1, 128), "constant-table hidden subset"),
                                           (32, F(1, 8), F(1, 128), "fixed-count fractional prior"),
                                           (63, F(1, 16), F(1, 256), "constant-table hidden subset"),
                                           (64, F(1, 16), F(1, 256), "fixed-count fractional prior")):
            self.assertEqual(check.rank_prior_case(prompts, tau, eps, F(1, 4), F(1, 4))["branch"], expected)
        one = check.rank_prior_case(1, F(1, 8), F(1, 128), F(1, 4), F(1, 4))
        self.assertEqual(one["hidden_subset_size"], 1)
        with self.assertRaises(ValueError):
            check.rank_prior_case(32, F(1, 8), F(1, 128), F(1, 16), F(1, 4))

    def test_log_endpoints_enclose_independent_high_precision_decimal(self):
        with localcontext() as context:
            context.prec = 90
            for delta in (F(1, 4), F(1, 20)):
                lo, hi = check.log_interval(delta)
                actual = (Decimal(delta.denominator)/Decimal(delta.numerator)).ln()
                self.assertLessEqual(Decimal(lo.numerator)/Decimal(lo.denominator), actual)
                self.assertGreaterEqual(Decimal(hi.numerator)/Decimal(hi.denominator), actual)
                self.assertLess(hi-lo, F(1, 2**70))

    def test_confidence_counterexample_uses_only_short_products(self):
        with patch.object(check, "comb", side_effect=AssertionError("no enormous binomial")), \
             patch.object(check, "exact_weights", side_effect=AssertionError("no enormous rank table")):
            for exponent in (7, 32):
                row = check.confidence_counterexample(exponent)
                self.assertEqual(row["prefix_product_factors"], 7)
                self.assertEqual(row["rank_weights_checked"], exponent)
                self.assertEqual(row["clipped_cost_lower"], exponent)
                self.assertLessEqual(F(row["tail_after_seven_ranks"]), F(1, 128))
                self.assertEqual(row["confidence_log_exact"], 4**exponent)
                self.assertFalse(row["delta_numerically_constructed"])

    def test_restricted_practical_case_keeps_its_original_declared_grid(self):
        row = check.practical_case(protocol()["practical_case"])
        self.assertEqual(row["budgets"], [16, 32, 64])
        self.assertTrue(row["different_declared_grid_from_original_study"])
        self.assertLessEqual(row["prefix_label_cost"], 2048)
        self.assertLessEqual(F(row["theorem_lower"]), F(row["available_upper"]))

    def test_invalid_geometry_and_inexact_values_are_rejected(self):
        for args in ((1, 8, [1, 8]), (1, 8, [2, 2]), (True, 8, [2]), (1, 1000000, [250000])):
            with self.assertRaises(ValueError):
                check.dense_grid_case(*args, F(1, 8), F(1, 128), F(1, 4))
        with self.assertRaises(ValueError):
            check.dense_grid_case(1, 8, [2], 0.125, F(1, 128), F(1, 4))
        with self.assertRaises(ValueError):
            check.reciprocal_expectation(1000000, 1, 1)

    def test_protocol_rejects_expansion_metadata_types_and_duplicate_keys(self):
        for key, value in (("version", True), ("version", 1.0), ("grid_max_pool_size", 1000000),
                           ("title", "changed"), ("taus", ["1e-10000000"])):
            changed = protocol()
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check.validate_protocol(changed)
        for raw in (b'{"version":1,"version":1}', b'{"number":NaN}', b" "*16385):
            with self.assertRaises(ValueError):
                check.parse_protocol(raw)
        self.assertEqual(check.validate_protocol(protocol()), protocol())

    def fixture(self, directory):
        root = Path(directory)
        for folder in ("experiments", "tests", "docs"):
            (root/folder).mkdir()
        for relative in ("experiments/check_finite_saturation.py", "tests/test_finite_saturation.py",
                         "experiments/check_sharp_cost.py", "experiments/finite_saturation_protocol.json"):
            (root/relative).write_bytes((ROOT/relative).read_bytes())
        for name in ("finite-saturation-theorem.md", "nonzero-minimax-theorem.md"):
            (root/"docs"/name).write_text("Temporary proof fixture.\n")
        return root, root/"experiments/finite_saturation_protocol.json"

    def test_six_pins_use_one_bounded_snapshot_and_detect_all_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def bounded(candidate):
                if candidate == path:
                    self.fail("protocol must only be read through the bounded stream")
                return original_read(candidate)
            with patch.object(check, "ROOT", root), \
                 patch.object(check, "__file__", str(root/"experiments/check_finite_saturation.py")), \
                 patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                 patch.object(check, "calculate", return_value={"fixture": True}), \
                 patch.object(Path, "read_bytes", bounded):
                result = check.build_results(None, path)
            self.assertEqual(len(result["source_sha256"]), 6)
            self.assertEqual(result["protocol_sha256"], hashlib.sha256(original_read(path)).hexdigest())
            self.assertEqual(result["protocol"], protocol())
            for relative in result["source_sha256"]:
                source = root/relative
                original = source.read_bytes()
                def mutate(_protocol):
                    source.write_bytes(original+b"\n")
                    return {}
                with patch.object(check, "ROOT", root), \
                     patch.object(check, "__file__", str(root/"experiments/check_finite_saturation.py")), \
                     patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                     patch.object(check, "calculate", side_effect=mutate):
                    with self.subTest(source=relative), self.assertRaisesRegex(RuntimeError, "changed"):
                        check.build_results(None, path)
                source.write_bytes(original)

    def test_overwrite_and_invalid_protocol_do_not_start_work_or_create_output(self):
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

    def test_runtime_arithmetic_guards_remain_enabled_under_optimization(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_finite_saturation as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.dense_grid_case(1,4,[1,4],F(1,8),F(1,128),F(1,4))\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
