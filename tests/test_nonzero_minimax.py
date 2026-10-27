"""Independent finite examples and integrity tests for the research checker."""

from contextlib import redirect_stderr
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_nonzero_minimax as check


ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/"experiments/nonzero_minimax_protocol.json").read_text())


class NonzeroMinimaxTests(unittest.TestCase):
    def test_weights_match_independent_subset_minima(self):
        for m in range(1, 7):
            for n in range(1, m+1):
                subsets = list(combinations(range(m), n))
                expected = tuple(F(sum(min(s) == r for s in subsets), len(subsets)) for r in range(m))
                self.assertEqual(check.exact_weights(m, n), expected)

    def test_likelihood_ratios_retain_terminal_zeros_without_zero_division(self):
        self.assertEqual(check.likelihood_ratios(4, 2, 4), (F(2), F(0), F(0)))
        self.assertEqual(check.likelihood_ratios(4, 4, 4), (F(1),))
        self.assertEqual(check.likelihood_ratios(4, 2, 2), (F(1),)*3)
        for m in range(1, 9):
            for a in range(1, m+1):
                for n in range(a, min(4*a, m+1)):
                    h = check.likelihood_ratios(m, a, n)
                    self.assertTrue(all(0 <= x <= 4 for x in h))
                    self.assertTrue(all(x >= y for x, y in zip(h, h[1:])))

    def test_sparse_grids_without_budget_one_have_exact_disjoint_bands(self):
        singleton = check.grid_geometry(8, [8])
        self.assertEqual(singleton["envelope_normalizer"], "1")
        self.assertEqual(singleton["representatives"], [8])
        sparse = check.grid_geometry(8, [2, 8])
        self.assertEqual(sparse["envelope_normalizer"], "7/4")
        self.assertEqual(sparse["representatives"], [2, 8])
        self.assertEqual([(b["first_rank"], b["last_rank"]) for b in sparse["bands"]], [(2, 4), (1, 1)])
        self.assertEqual([b["mass"] for b in sparse["bands"]], ["15/28", "1"])
        for grid in [[], [0], [9], [2, 2], [8, 2]]:
            with self.assertRaises(ValueError):
                check.grid_geometry(8, grid)

    def test_layer_cake_matrix_identity_and_signed_extrema(self):
        # Independent prefix coordinates expose both a missing terminal term
        # and a reversal of the summation-by-parts coefficients.
        for h in [(F(4), F(3), F(1), F(0)), (F(1),)*3, (F(4),)]:
            coefficients = check.layer_cake(h)
            self.assertEqual(sum(coefficients), h[0])
            for column in range(len(h)):
                prefix = [F(int(i >= column)) for i in range(len(h))]
                self.assertEqual(sum(c*x for c, x in zip(coefficients, prefix)), h[column])
            for prefix in product((-1, 1), repeat=len(h)):
                increments = [F(prefix[0])]+[F(prefix[i]-prefix[i-1]) for i in range(1, len(h))]
                direct = sum(x*y for x, y in zip(h, increments))
                transformed = sum(c*x for c, x in zip(coefficients, prefix))
                self.assertEqual(direct, transformed)
                self.assertLessEqual(abs(direct), 4)
        with self.assertRaises(ValueError):
            check.layer_cake((F(1), F(2)))

    def test_small_exhaustive_kernels_include_every_endpoint_and_sparse_grid(self):
        ratios = check.ratio_checks(3)
        self.assertEqual(ratios["ratio_cases"], 10)
        self.assertEqual(ratios["summation_by_parts_columns"], 20)
        self.assertEqual(ratios["target_terminal_zeros"], 5)
        grids = check.grid_checks(3)
        self.assertEqual(grids["nonempty_grids"], 11)
        self.assertEqual(grids["strict_disjoint_bands"], 11)
        self.assertEqual(grids["grids_without_budget_one"], 4)

    def test_conditional_laws_match_independent_fixed_profile_enumeration(self):
        # Two independent ranks, with only rank zero changed by the alternative.
        # Conditioning is on an interleaved, non-prefix ordering of prompt IDs.
        prompts = 6
        transcript = [(0, 4, 1), (1, 1, 0), (0, 0, 0)]
        for changed_count in [2, 3]:
            profiles = product(combinations(range(prompts), changed_count), combinations(range(prompts), 2))
            compatible = [tuple(map(set, table)) for table in profiles
                          if all(int(p in table[r]) == y for r, p, y in transcript)]
            observed = F(sum(3 in table[0] for table in compatible), len(compatible))
            safe, alternative = check.conditional_probabilities(prompts, 2, 3, 2, 1)
            self.assertEqual(observed, safe if changed_count == 2 else alternative)
            for table in compatible:
                # For equal fixed rank counts every permutation has the same risk.
                if changed_count == 2:
                    for n in (1, 2):
                        risk = sum(check.exact_weights(2, n)[r]*int(p in table[r])/prompts
                                   for r in range(2) for p in range(prompts))
                        self.assertEqual(risk, F(1, 3))

    def test_hypergeometric_majorant_and_support_include_cap_boundary(self):
        u, v = check.conditional_probabilities(16, 2, 3, 1, 1)
        self.assertEqual((u, v), (F(1, 15), F(2, 15)))
        bound = check.conditional_kl_majorant(16, 2, 3, 1, 1)
        self.assertEqual(bound, F(1, 26))
        self.assertLessEqual(bound, F(1, 2))  # 16 (q-p)^2 / p
        with self.assertRaises(ValueError):
            check.conditional_probabilities(16, 2, 3, 3, 3)
        small = check.conditional_checks([16])
        self.assertEqual(small["comparisons"], 5)
        self.assertEqual(small["cap_boundary_comparisons"], 4)

    def test_profile_rounding_preserves_safe_and_strict_unsafe_counts(self):
        counts = check.profile_counts(257, F(1, 8), F(1, 128))
        self.assertEqual((counts["safe_count"], counts["increment_count"], counts["unsafe_count"], counts["cap"]), (30, 17, 47, 15))
        self.assertLessEqual(F(30, 257), F(15, 128))
        self.assertGreater(F(30, 257)+F(17, 257)*F(1, 4), F(1, 8))
        integral = check.profile_counts(256, F(1, 8), F(1, 128))
        self.assertEqual((integral["safe_count"], integral["increment_count"]), (30, 16))

    def test_symbolic_certificate_has_outward_finite_lower_bound(self):
        case = check.lower_certificate(F(1, 8), F(1, 128), F(1, 4), 1)
        self.assertEqual(case["prompts"], 22714)
        self.assertEqual((case["safe_count"], case["increment_count"], case["cap"]), (2661, 1420, 1330))
        lo, hi = map(F, (case["log_interval"]["lower"], case["log_interval"]["upper"]))
        g = F(case["finite_band_lower"])
        self.assertGreaterEqual(g, F(case["theorem_band_target_upper"]))
        self.assertLessEqual(g, (lo-F(case["log_two_upper"]))/(1296*F(1,128)**2/F(2661,22714)+hi/1330))
        self.assertGreater(case["prompts"], 10000)

    def test_stages_have_resolved_ceilings_and_squared_radius_certificate(self):
        case = check.stage_certificate(F(1, 8), F(1, 128), F(1, 4), 3)
        stages = case["stages"]
        self.assertEqual(len(stages), 3)
        self.assertEqual(stages[0]["draws_lower"], 29072700)
        for stage in stages:
            self.assertEqual(stage["draws_lower"], stage["draws_upper"])
            self.assertLess(F(stage["radius_squared_left"]), F(stage["radius_squared_right"]))
            self.assertGreater(F(stage["radius_linear_slack"]), 0)
        self.assertLessEqual(F(case["expected_draws_upper"]), F(case["three_A_L_lower"]))

    def test_ambiguous_stage_ceiling_is_bracketed_instead_of_silently_selected(self):
        lo, hi = check.log_interval(F(1, 4))
        # A deliberately wider, still valid log enclosure straddles ceilings.
        with patch.object(check, "log_interval", return_value=(lo-F(1, 8388608), hi+F(1, 8388608))):
            stage = check.stage_certificate(F(1, 8), F(1, 128), F(1, 4), 1)["stages"][0]
        self.assertLess(stage["draws_lower"], stage["draws_upper"])
        self.assertEqual(stage["ceiling_status"], "explicit_interval")

    def test_practical_geometry_reports_failed_lower_condition_and_census(self):
        case = check.practical_case(protocol()["practical_case"])
        self.assertFalse(case["lower_replication_condition_holds"])
        self.assertEqual(case["census_cap"], 2048)
        self.assertGreater(case["first_stage_draws_lower"], 2048)
        self.assertTrue(case["census_before_first_stage"])
        self.assertEqual(case["cost_upper_with_census"], "2048")

    def test_result_counts_distinct_schedules_separately_from_copied_entries(self):
        # Keep exhaustive matrix kernels separate from this orchestration test.
        # Actual symbolic certificates and stage arithmetic still run here.
        with patch.object(check, "ratio_checks", return_value={}), patch.object(check, "grid_checks", return_value={}), patch.object(check, "conditional_checks", return_value={}):
            result = check.calculate(protocol())
        self.assertEqual(result["certificate_count"], 16)
        self.assertEqual(result.get("certificate_checks"), {
            "distinct_stage_schedules": 8, "stage_checks": 128,
            "stored_stage_entries": 256, "symbolic_profile_certificates": 16,
        })
        for row in result["analytical_certificates"]:
            for stage in row["stage_certificate"]["stages"]:
                self.assertEqual(stage["ceiling_status"], "resolved")

    def test_protocol_rejects_any_schedule_or_metadata_mutation_before_work(self):
        for key, value in [("ratio_max_pool_size", 1000000000), ("stages", 1),
                           ("version", True), ("version", 1.0), ("certificate_taus", ["1e-100000000"]),
                           ("title", "altered")]:
            changed = protocol()
            changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                check.validate_protocol(changed)
        duplicate = b'{"version": 1, "version": 1}'
        with self.assertRaises(ValueError):
            check.parse_protocol(duplicate)
        with self.assertRaises(ValueError):
            check.parse_protocol(b" "*(check.MAX_PROTOCOL_BYTES+1))
        self.assertEqual(check.validate_protocol(protocol()), protocol())

    def fixture(self, directory):
        root = Path(directory)
        for parent in ("tests", "docs", "experiments"):
            (root/parent).mkdir()
        (root/"tests/test_nonzero_minimax.py").write_bytes(Path(__file__).read_bytes())
        (root/"docs/nonzero-minimax-theorem.md").write_text("Temporary proof fixture.\n")
        (root/"experiments/check_sharp_cost.py").write_bytes((ROOT/"experiments/check_sharp_cost.py").read_bytes())
        path = root/"experiments/nonzero_minimax_protocol.json"
        path.write_bytes((ROOT/"experiments/nonzero_minimax_protocol.json").read_bytes())
        return root, path

    def test_result_pins_five_sources_and_uses_one_protocol_snapshot(self):
        # The arithmetic kernels are exercised above. Avoid the full frozen
        # matrix here: the publication run must follow independent review.
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            with patch.object(check, "ROOT", root), patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), patch.object(check, "calculate", return_value={"bounded_fixture": True}):
                first = check.build_results(None, path)
                second = check.build_results(protocol(), path)
            self.assertEqual(first, second)
            self.assertEqual(len(first["source_sha256"]), 5)
            self.assertEqual(first["protocol_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(first["protocol"], protocol())
            self.assertIn("experiments/check_sharp_cost.py", first["source_sha256"])
            self.assertIn("docs/nonzero-minimax-theorem.md", first["source_sha256"])

    def test_source_drift_and_protocol_replacement_abort_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            for file in [path, root/"experiments/check_sharp_cost.py", root/"docs/nonzero-minimax-theorem.md"]:
                original = file.read_bytes()
                def mutate(_protocol):
                    file.write_bytes(original+b"\n")
                    return {}
                with patch.object(check, "ROOT", root), patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), patch.object(check, "calculate", side_effect=mutate):
                    with self.assertRaisesRegex(RuntimeError, "changed"):
                        check.build_results(None, path)
                file.write_bytes(original)
            changed = protocol()
            changed["stages"] = 2
            with patch.object(check, "ROOT", root), self.assertRaises(ValueError):
                check.build_results(changed, path)

    def test_protocol_integrity_reread_preserves_the_input_byte_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def no_unbounded_protocol_read(candidate):
                if candidate == path:
                    self.fail("protocol integrity reread must remain bounded if the file grows")
                return original_read(candidate)
            with patch.object(check, "ROOT", root), patch.object(check, "calculate", return_value={}), patch.object(Path, "read_bytes", no_unbounded_protocol_read):
                result = check.build_results(None, path)
            self.assertEqual(result["protocol"], protocol())

    def test_cli_overwrite_and_invalid_protocol_create_no_output(self):
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

    def test_runtime_checks_remain_active_under_optimized_python(self):
        code = ("from fractions import Fraction as F\nfrom unittest.mock import patch\n"
                "from experiments import check_nonzero_minimax as c\n"
                "with patch.object(c, 'exact_weights', return_value=(F(0),)*4):\n"
                "    c.likelihood_ratios(4, 2, 4)\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
