"""Independent small checks for the finite-density arithmetic artifact."""

from contextlib import redirect_stderr
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
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

from experiments import check_finite_density as check


ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/"experiments/finite_density_protocol.json").read_text())


class FiniteDensityTests(unittest.TestCase):
    def test_flattened_weights_match_subset_enumeration(self):
        for m in range(1, 8):
            for n in range(1, m+1):
                winners = [0]*m
                for subset in itertools.combinations(range(m), n):
                    winners[min(subset)] += 1
                for prompts in (1, 3):
                    expected = tuple(F(count, comb(m, n)*prompts)
                                     for count in winners for _ in range(prompts))
                    self.assertEqual(check.flattened_weights(prompts, m, n), expected)

    def test_signed_abel_and_noninteger_boundary_include_terminal_zero(self):
        weights = (F(2, 3), F(1, 3), F(0))
        increments = (F(-2, 7), F(5, 11), F(-3, 5))
        result = check.abel_identity(weights, increments, F(1, 8), F(3, 2))
        expected = sum((a*b for a, b in zip(weights, increments)), F(0))
        self.assertEqual(result["weighted_sum"], expected)
        self.assertEqual(result["prefix_sum"], expected)
        self.assertEqual(result["boundary_value"], F(1, 8))
        self.assertEqual(result["coefficients"], (F(1, 3), F(1, 3), F(0)))
        with self.assertRaises(ValueError):
            check.abel_identity((F(1, 3), F(2, 3)), (F(0), F(0)), F(1, 8), F(1))

    def test_binary_event_counts_are_exact_and_all_budgets_share_event(self):
        case = check.binary_case(2, 3, F(1, 4), F(1, 8), F(1, 8))
        bad_boundary = [0]*7
        bad_risk = [0]*7
        p, eps = F(1, 8), F(1, 8)
        for labels in itertools.product((0, 1), repeat=6):
            boundary_bad = any(sum(labels[:k])-k*p > eps*(k+2)/2 for k in range(1, 7))
            risk_bad = False
            for n in range(1, 4):
                risk = sum((F(comb(3-r, n-1), comb(3, n))*F(sum(labels[2*(r-1):2*r]), 2)
                            for r in range(1, 5-n)), F(0))
                risk_bad |= risk > p+eps
            bad_boundary[sum(labels)] += boundary_bad
            bad_risk[sum(labels)] += risk_bad
            self.assertFalse(risk_bad and not boundary_bad)
        self.assertEqual(case["boundary_failure_counts_by_ones"], bad_boundary)
        self.assertEqual(case["risk_failure_counts_by_ones"], bad_risk)
        probability = sum((count*p**s*(1-p)**(6-s) for s, count in enumerate(bad_boundary)), F(0))
        self.assertEqual(F(case["boundary_failure_probability"]), probability)
        self.assertFalse(case["exponential_bound_numerically_checked"])

    def test_log_wrapper_accepts_four_fifths_and_encloses_independent_decimal(self):
        with localcontext() as context:
            context.prec = 90
            for value in (F(4, 5), F(1, 4), F(1, 20), F(1, 80)):
                lo, hi = check.log_bounds(value)
                actual = (Decimal(value.denominator)/Decimal(value.numerator)).ln()
                self.assertLessEqual(Decimal(lo.numerator)/Decimal(lo.denominator), actual)
                self.assertGreaterEqual(Decimal(hi.numerator)/Decimal(hi.denominator), actual)
        self.assertLess(check.log_bounds(F(4, 5))[1], F(1, 4))

    def test_product_prior_parameters_and_binary_kl_majorant(self):
        for tau in (F(1, 8), F(1, 16)):
            for ratio in (F(1, 16), F(1, 64)):
                eps = tau*ratio
                p, q, kappa, majorant = check.product_parameters(tau, eps)
                self.assertEqual((p, q), (tau-2*eps, tau+10*eps))
                self.assertGreaterEqual(p, 7*tau/8)
                self.assertLess(q, F(1, 4))
                self.assertLess(majorant, kappa)
                with localcontext() as context:
                    context.prec = 60
                    pd, qd = (Decimal(v.numerator)/Decimal(v.denominator) for v in (p, q))
                    kl = pd*(pd/qd).ln()+(1-pd)*((1-pd)/(1-qd)).ln()
                    self.assertLess(kl, Decimal(majorant.numerator)/Decimal(majorant.denominator))

    def test_symbolic_density_and_cap_endpoints_are_outward(self):
        case = check.density_certificate(F(1, 8), F(1, 128), F(1, 4), {"prompts": 1, "max_budget": 16})
        self.assertGreater(case["pool_size"], 100000)
        self.assertEqual(case["cap_lower"], case["cap_upper"])
        self.assertEqual(case["ceiling_status"], "resolved")
        self.assertGreaterEqual(F(case["effective_population"]), F(case["required_population_upper"]))
        self.assertGreater(F(case["information_lower"]), F(case["information_upper_if_small_cost"]))
        self.assertTrue(case["density_condition_verified"])
        self.assertEqual(check.ceil_fraction(F(6, 3)), 2)
        self.assertEqual(check.ceil_fraction(F(7, 3)), 3)

    def test_ambiguous_cap_is_explicitly_bracketed(self):
        original = check.log_bounds
        def wider(value):
            lo, hi = original(value)
            return (lo-F(1, 50), hi+F(1, 50)) if value == F(1, 20) else (lo, hi)
        with patch.object(check, "log_bounds", side_effect=wider):
            case = check.density_certificate(F(1, 8), F(1, 512), F(1, 20), {"prompts": 1, "max_budget": 16})
        self.assertLess(case["cap_lower"], case["cap_upper"])
        self.assertEqual(case["ceiling_status"], "explicit_interval")

    def test_tails_and_minimal_prefix_match_independent_subsets(self):
        for m in range(1, 9):
            for n in range(1, m+1):
                subsets = tuple(itertools.combinations(range(1, m+1), n))
                tails = tuple(F(sum(min(s) > k for s in subsets), len(subsets)) for k in range(m+1))
                self.assertEqual(tuple(check.exact_tail(m, n, k) for k in range(m+1)), tails)
                for eps in (F(1, 8), F(1, 32)):
                    k = check.minimal_prefix(m, n, eps)
                    self.assertLessEqual(tails[k], eps)
                    self.assertTrue(k == 0 or tails[k-1] > eps)

    def test_symbolic_counterexample_uses_only_short_product(self):
        rows = [check.counterexample(k) for k in (8, 12, 16, 24)]
        ratios = [F(row["baseline_to_prefix_ratio_lower"]) for row in rows]
        self.assertTrue(all(x < y for x, y in zip(ratios, ratios[1:])))
        for row in rows:
            self.assertEqual(row["product_factors"], row["exponent"])
            self.assertLessEqual(F(row["tail_after_prefix"]), F(row["epsilon"]))
            self.assertEqual(row["positive_support"], row["pool_size"]//2+1)

    def test_practical_case_fails_density_and_reaches_full_prefix(self):
        case = check.practical_case(protocol()["practical_case"])
        self.assertFalse(case["density_condition_holds"])
        self.assertEqual(case["prefix_ranks"], 64)
        self.assertEqual(case["prefix_label_cost"], 2048)

    def test_orchestration_counts_eight_profiles_and_sixteen_symbolic_geometries(self):
        # Keep the exhaustive finite matrices out of this orchestration test.
        # The actual symbolic certificates still exercise all frozen profiles.
        with patch.object(check, "abel_checks", return_value={}), patch.object(check, "binary_checks", return_value={}), patch.object(check, "tail_checks", return_value={}):
            result = check.calculate(protocol())
        self.assertEqual(result["profile_count"], 8)
        self.assertEqual(result["density_certificate_count"], 16)
        for profile in result["symbolic_profiles"]:
            for row in profile["geometries"]:
                self.assertEqual(row["ceiling_status"], "resolved")
                self.assertGreater(F(row["information_lower"]), F(row["information_upper_if_small_cost"]))

    def test_protocol_freeze_rejects_metadata_types_duplicates_and_expansion(self):
        for key, value in (("version", True), ("version", 1.0), ("abel_max_pool_size", 1000000),
                           ("title", "changed"), ("certificate_taus", ["1e-10000000"])):
            changed = protocol()
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check.validate_protocol(changed)
        with self.assertRaises(ValueError):
            check.parse_protocol(b'{"version": 1, "version": 1}')
        with self.assertRaises(ValueError):
            check.parse_protocol(b" "*(check.MAX_PROTOCOL_BYTES+1))
        self.assertEqual(check.validate_protocol(protocol()), protocol())

    def fixture(self, directory):
        root = Path(directory)
        for name in ("experiments", "tests", "docs"):
            (root/name).mkdir()
        (root/"tests/test_finite_density.py").write_bytes(Path(__file__).read_bytes())
        for name in ("finite-density-theorem.md", "nonzero-minimax-theorem.md"):
            (root/"docs"/name).write_text("Temporary proof fixture.\n")
        (root/"experiments/check_sharp_cost.py").write_bytes((ROOT/"experiments/check_sharp_cost.py").read_bytes())
        path = root/"experiments/finite_density_protocol.json"
        path.write_bytes((ROOT/"experiments/finite_density_protocol.json").read_bytes())
        return root, path

    def test_six_source_pins_and_single_bounded_protocol_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def bounded(candidate):
                if candidate == path:
                    self.fail("protocol reread must remain bounded")
                return original_read(candidate)
            with patch.object(check, "ROOT", root), patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), patch.object(check, "calculate", return_value={"fixture": True}), patch.object(Path, "read_bytes", bounded):
                result = check.build_results(None, path)
            self.assertEqual(len(result["source_sha256"]), 6)
            self.assertEqual(result["protocol_sha256"], hashlib.sha256(original_read(path)).hexdigest())
            self.assertEqual(result["protocol"], protocol())

    def test_source_and_protocol_drift_abort_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            for source in (path, root/"docs/finite-density-theorem.md", root/"docs/nonzero-minimax-theorem.md", root/"experiments/check_sharp_cost.py"):
                original = source.read_bytes()
                def mutate(_protocol):
                    source.write_bytes(original+b"\n")
                    return {}
                with patch.object(check, "ROOT", root), patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), patch.object(check, "calculate", side_effect=mutate):
                    with self.assertRaisesRegex(RuntimeError, "changed"):
                        check.build_results(None, path)
                source.write_bytes(original)

    def test_overwrite_and_invalid_protocol_fail_before_output_creation(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            root, path = self.fixture(directory)
            out = root/"result.json"
            out.write_bytes(b"preserve")
            with patch.object(check, "build_results", side_effect=AssertionError("work started")):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(out)]), 0)
            self.assertEqual(out.read_bytes(), b"preserve")
            path.write_text('{"invalid": true}')
            absent = root/"new-parent/result.json"
            self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(absent)]), 0)
            self.assertFalse(absent.parent.exists())

    def test_runtime_requirements_survive_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_finite_density as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.flattened_weights(1, 4, 2)\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
