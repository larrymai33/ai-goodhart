"""Small independent arithmetic and integrity tests for sharp cost checks."""

from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_sharp_cost as check


ROOT = Path(__file__).resolve().parents[1]


def miniature_protocol():
    protocol = json.loads((ROOT/"experiments/sharp_cost_protocol.json").read_text())
    protocol.update(inverse_max_block_size=3, inverse_deltas=["1/4", "1/20"],
                    large_inverse_cases=[{"block_size": 40, "bad_subset_size": 4, "delta": "1/4"}],
                    certificate_geometries=[{"pool_size": 4, "maximum_budget": 3}],
                    certificate_k=[8, 16], certificate_deltas=["1/4"])
    return protocol


class SharpCostTests(unittest.TestCase):
    def test_exact_rank_weights_match_subset_enumeration(self):
        for m in range(1, 7):
            for n in range(1, m+1):
                subsets = list(combinations(range(m), n))
                actual = tuple(F(sum(min(subset) == r for subset in subsets), len(subsets)) for r in range(m))
                self.assertEqual(check.exact_weights(m, n), actual)

    def test_log_interval_contains_independent_longer_positive_series(self):
        def series(z):
            total = sum((2*z**(2*j+1)/F(2*j+1) for j in range(48)), F(0))
            return total, total+2*z**97/(97*(1-z*z))
        for delta in [F(1, 4), F(1, 20), F(1, 1000)]:
            reciprocal = 1/delta
            scale = 0
            while 2**(scale+1) <= reciprocal:
                scale += 1
            y = reciprocal/2**scale
            lo2, hi2 = series(F(1, 3))
            loy, hiy = series((y-1)/(y+1))
            lower, upper = check.log_interval(delta)
            self.assertLessEqual(lower, scale*lo2+loy)
            self.assertGreaterEqual(upper, scale*hi2+hiy)
            self.assertLessEqual(upper-lower, F(2, 1 << 80))
            self.assertEqual((lower*(1 << 80)).denominator, 1)
            self.assertEqual((upper*(1 << 80)).denominator, 1)

    def test_directed_rounding_and_serialization_limit(self):
        unit = F(1, 1 << 80)
        for value in [F(1, 3), F(-1, 3), 7*unit, F(10**20, 7)]:
            down, up = check.round_down(value), check.round_up(value)
            self.assertLessEqual(down, value)
            self.assertGreaterEqual(up, value)
            self.assertLess(value-down, unit)
            self.assertLess(up-value, unit)
        with self.assertRaises(ValueError):
            check.fraction_text(F(1, 1 << 2049))

    def test_exact_hypergeometric_inverse_and_finite_bound_endpoints(self):
        self.assertEqual(check.exact_inverse(5, 2, F(1, 4)), F(9, 4))
        self.assertEqual(check.exact_inverse(5, 1, F(1, 4)), F(15, 4))
        self.assertEqual(check.exact_inverse(5, 5, F(1, 4)), F(3, 4))
        lower, _ = check.log_interval(F(1, 4))
        self.assertEqual(check.finite_lower_bound(5, 5, lower), 0)
        for d in range(1, 9):
            for b in range(1, d+1):
                inverse = check.exact_inverse(d, b, F(1, 4))
                self.assertLessEqual(check.finite_lower_bound(d, b, lower), inverse)

    def test_greedy_endpoint_bins_cover_and_witness_unsafe_subsets(self):
        for m, n, eta in [(1, 1, F(1, 8)), (6, 4, F(1, 2)), (8, 8, F(1, 8))]:
            bins = check.value_bins(m, n, eta)
            envelope = [max(check.exact_weights(m, budget)[r] for budget in range(1, n+1)) for r in range(m)]
            self.assertEqual([r for bin in bins for r in range(bin["first_rank"], bin["last_rank"]+1)], list(range(1, m+1)))
            for bin in bins:
                start, stop = bin["first_rank"], bin["last_rank"]
                end = F(bin["endpoint_envelope"])
                self.assertEqual(envelope[stop-1], end)
                self.assertLessEqual(envelope[start-1], (1+eta)*end)
                if stop < m:
                    self.assertGreater(envelope[start-1], (1+eta)*envelope[stop])
                row = check.exact_weights(m, bin["witness_budget"])
                self.assertEqual(row[stop-1], end)
                tau = (stop-start+1)*end/3
                bad_size = tau//end+1
                for subset in combinations(range(start-1, stop), bad_size):
                    self.assertGreater(sum((row[r] for r in subset), F(0)), tau)

    def test_certificate_rounds_each_lower_before_summing_symbolic_population(self):
        m, n, k, delta = 8, 8, 16, F(1, 20)
        record = check.cost_certificate(m, n, k, delta)
        p, tau = record["prompts"], F(record["tau"])
        lo, hi = check.log_interval(delta)
        rounded, exact_total = F(0), F(0)
        for bin in check.value_bins(m, n, F(1, k)):
            endpoint = F(bin["endpoint_envelope"])
            count = bin["last_rank"]-bin["first_rank"]+1
            if count*endpoint >= k*tau:
                d, b = p*count, tau//(endpoint/p)+1
                exact = lo*(d-b)/(b+lo)
                exact_total += exact
                rounded += check.round_down(exact)
        self.assertEqual(F(record["lower_bound"]), rounded)
        # This chosen case distinguishes rounding each bin from rounding the
        # final exact sum; the production path must use the former.
        self.assertLess(rounded, check.round_down(exact_total))
        self.assertEqual(F(record["upper_bound"]), check.round_up(hi*F(record["envelope_normalizer"])/tau))
        self.assertEqual(F(record["ratio_upper"]), F(record["upper_bound"])/rounded)
        self.assertLessEqual(F(record["rho_upper"]), F(1, k))
        big = check.cost_certificate(128, 128, 2048, F(1, 20))
        self.assertGreater(big["items"], 10**12)
        self.assertLessEqual(big["bin_count"], 128)
        self.assertLess(len(json.dumps(big)), 20000)

    def test_decimal_displays_are_outward_for_sensitive_cases(self):
        certificate = check.cost_certificate(8, 8, 16, F(1, 20))
        for field, upward in [("lower_bound", False), ("upper_bound", True), ("ratio_upper", True)]:
            shown, exact = F(certificate["display"][field]), F(certificate[field])
            with self.subTest(field=field):
                if upward:
                    self.assertGreaterEqual(shown, exact)
                else:
                    self.assertLessEqual(shown, exact)
        inverse = check._large_inverse_case({"block_size": 40, "bad_subset_size": 4, "delta": "1/4"})
        expected = {
            "finite_lemma_lower": (inverse["finite_lemma_lower"], False),
            "inverse_lower": (inverse["exact_inverse_enclosure"]["lower"], False),
            "inverse_upper": (inverse["exact_inverse_enclosure"]["upper"], True),
            "lemma_over_inverse_lower": (inverse["lemma_over_inverse_lower"], False),
        }
        for field, (exact_text, upward) in expected.items():
            shown, exact = F(inverse["display"][field]), F(exact_text)
            with self.subTest(field=field):
                if upward:
                    self.assertGreaterEqual(shown, exact)
                else:
                    self.assertLessEqual(shown, exact)

    def test_invalid_protocol_and_rational_grammar_fail_before_conversion(self):
        base = miniature_protocol()
        variants = []
        for key, value in [("inverse_max_block_size", 65), ("log_series_terms", 31),
                           ("dyadic_rounding_bits", 80.0), ("certificate_k", [2049]),
                           ("certificate_deltas", ["1/1000"])]:
            changed = deepcopy(base)
            changed[key] = value
            variants.append(changed)
        changed = deepcopy(base)
        changed["theorem"]["confidence_range"] = "0<delta<1"
        variants.append(changed)
        for protocol in variants:
            with self.assertRaises(ValueError):
                check.validate_protocol(protocol)
        for text in ["1e10000000000", "1e-10000000000", "0.25", "1/0", "01", "1/02", "-1"]:
            changed = deepcopy(base)
            changed["inverse_deltas"] = [text]
            with patch.object(check, "F", side_effect=AssertionError("Fraction called")) as fraction:
                with self.assertRaises(ValueError):
                    check.validate_protocol(changed)
                fraction.assert_not_called()

    def fixture(self, directory):
        root = Path(directory)
        (root/"tests").mkdir()
        (root/"docs").mkdir()
        (root/"tests/test_sharp_cost.py").write_bytes(Path(__file__).read_bytes())
        for name in ["sharp-cost-theorem.md", "sharp-envelope.md"]:
            (root/"docs"/name).write_text("Temporary proof fixture for bounded unit tests.\n")
        path = root/"protocol.json"
        path.write_text(json.dumps(miniature_protocol()))
        return root, path

    def test_miniature_result_is_deterministic_and_pins_five_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            with patch.object(check, "ROOT", root):
                result = check.build_results(miniature_protocol(), path)
                repeated = check.build_results(miniature_protocol(), path)
            self.assertEqual(result, repeated)
            self.assertEqual(result["inverse_checks"]["comparisons"], 12)
            self.assertEqual(len(result["large_inverse_checks"]), 1)
            self.assertEqual(len(result["cost_certificates"]), 2)
            self.assertEqual(len(result["source_sha256"]), 5)
            self.assertEqual(result["source_sha256"]["protocol.json"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_source_mutation_and_output_failure_leave_no_artifact(self):
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
            out = root/"result.json"
            out.write_bytes(b"preserve")
            with patch.object(check, "ROOT", root), patch.object(check, "build_results", side_effect=AssertionError("work started")):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(out)]), 0)
            self.assertEqual(out.read_bytes(), b"preserve")
            bad = miniature_protocol()
            bad["log_series_terms"] = 1
            path.write_text(json.dumps(bad))
            destination = root/"new-parent/result.json"
            with patch.object(check, "ROOT", root):
                self.assertNotEqual(check.main(["--protocol", str(path), "--out", str(destination)]), 0)
            self.assertFalse(destination.parent.exists())

    def test_checks_remain_active_under_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_sharp_cost as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.value_bins(4,4,F(1,8))\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
