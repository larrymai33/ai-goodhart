"""Independent tests for the original-decision finite lower certificate."""

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

try:
    check = importlib.import_module("experiments.check_finite_decision")
except ModuleNotFoundError as error:
    if error.name != "experiments.check_finite_decision":
        raise
    check = None

ROOT = Path(__file__).resolve().parents[1]


def protocol():
    return json.loads((ROOT/"experiments/finite_decision_protocol.json").read_text())


def brute_stopping_pairs(size, count, added):
    """Explicit fixed subsets and prefix trees; no compressed-state formula."""
    null = tuple(set(s) for s in itertools.combinations(range(size), count))
    alternative = tuple(set(s) for s in itertools.combinations(range(size), count+added))
    def recurse(prefix):
        a = F(sum(all((i in table) == bit for i, bit in enumerate(prefix)) for table in null), len(null))
        b = F(sum(all((i in table) == bit for i, bit in enumerate(prefix)) for table in alternative), len(alternative))
        if not a or not b:
            return {(F(0), F(0))}
        pairs = {(F(0), b)}
        if len(prefix) < size:
            left, right = recurse(prefix+(False,)), recurse(prefix+(True,))
            pairs.update((a+c0+c1, q0+q1) for (c0, q0), (c1, q1) in itertools.product(left, right))
        return pairs
    return recurse(())


class FiniteDecisionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(check, "finite-decision checker implementation is missing")

    def test_hand_solvable_extremes_and_zero_multiplier(self):
        for size in range(1, 9):
            for multiplier in (0, 1, 3, 10, 100):
                one = check.exact_dual(size, 0, 1, multiplier)
                all_changed = check.exact_dual(size, 0, size, multiplier)
                self.assertEqual(F(one["value_numerator"], one["denominator"]), min(multiplier, size))
                self.assertEqual(F(all_changed["value_numerator"], all_changed["denominator"]), min(multiplier, 1))
        row = check.exact_dual(2, 1, 1, 2)
        self.assertEqual(F(row["value_numerator"], row["denominator"]), F(3, 2))

    def test_integer_dp_matches_independent_exhaustive_stopping_choices(self):
        for size in range(2, 6):
            for count in range(size):
                for added in range(1, size-count+1):
                    pairs = brute_stopping_pairs(size, count, added)
                    for multiplier in (0, 1, 2, 4, 8):
                        row = check.exact_dual(size, count, added, multiplier)
                        expected = min(cost+multiplier*error for cost, error in pairs)
                        self.assertEqual(F(row["value_numerator"], row["denominator"]), expected)
                        policy = (F(row["policy_cost_numerator"], row["denominator"]),
                                  F(row["policy_error_numerator"], row["denominator"]))
                        self.assertIn(policy, pairs)
                        self.assertEqual(row["null_certificate_numerator"], row["denominator"])

    def test_arbitrary_coordinate_support_oracle_matches_independent_policy_pairs(self):
        for size, count, added in ((3, 0, 1), (4, 1, 1), (5, 1, 2), (6, 2, 1)):
            pairs = brute_stopping_pairs(size, count, added)
            for multiplier in (1, 3, 10, 100):
                expected = min(cost+multiplier*error for cost, error in pairs)
                self.assertEqual(check.explicit_coordinate_value(size, count, added, multiplier), expected)

    def test_ordered_prefix_mass_is_not_multiplied_by_state_path_count(self):
        row = check.ordered_masses(6, 2, 1, 2, 1)
        self.assertEqual(F(row["null_mass"], row["denominator"]), F(4, 15))
        self.assertEqual(F(row["alternative_mass"], row["denominator"]), F(3, 10))
        # Both 01 and 10 share this state; each has these masses separately.
        self.assertNotEqual(F(row["null_mass"], row["denominator"]), F(8, 15))

    def test_original_grid_tail_geometry_and_strict_alternative_are_exact(self):
        row = check.geometry_certificate(protocol()["geometry"])
        self.assertEqual(row["declared_budgets"], [1, 2, 4, 8, 16, 32, 64])
        self.assertEqual(row["tail_cells"], 1024)
        self.assertEqual(F(row["null_uniform_risk"]), F(3, 32))
        self.assertEqual(F(row["null_uniform_risk"]), F(1, 10)-F(1, 160))
        self.assertEqual(F(row["alternative_excess_above_tau"]), F(1, 10240))
        self.assertEqual(row["domination_atom_checks"], 64*32)
        self.assertFalse(row["different_declared_grid_from_original_study"])

    def test_direct_subset_winners_match_frozen_weight_helper_on_small_pools(self):
        for size in range(1, 8):
            for budget in range(1, size+1):
                subsets = tuple(itertools.combinations(range(size), budget))
                expected = tuple(F(sum(min(s) == r for s in subsets), len(subsets)) for r in range(size))
                self.assertEqual(tuple(check.exact_weights(size, budget)), expected)

    def test_decimal_enclosures_and_competitive_ratio_round_outward(self):
        for value, lower, upper in ((F(1, 3), "0.333333333", "0.333333334"),
                                    (F(-1, 3), "-0.333333334", "-0.333333333"),
                                    (F(5, 2), "2.500000000", "2.500000000")):
            self.assertEqual(check.decimal_bound(value), lower)
            self.assertEqual(check.decimal_bound(value, upward=True), upper)
        row = check.dual_certificate(2, 1, 1, 2, F(1, 4), 4)
        self.assertEqual(F(row["dual_lower_exact"]), 1)
        self.assertEqual(row["census_to_lower_ratio_upper"], "4.000000000")
        self.assertGreaterEqual(row["rounded_lower_integer_residual"], 0)

    def test_actual_intermediate_bit_cap_and_population_guards(self):
        row = check.exact_dual(16, 3, 2, 100)
        self.assertEqual(row["null_possible_states"], 4*14)
        self.assertGreaterEqual(row["maximum_integer_bits"], row["denominator"].bit_length())
        self.assertEqual(len(row["state_sha256"]), 64)
        self.assertGreater(row["certified_null_state_checks"], 0)
        with patch.object(check, "MAX_INTEGER_BITS", 4):
            with self.assertRaises(RuntimeError):
                check.exact_dual(16, 3, 2, 100)
        for args in ((True, 0, 1, 1), (1025, 0, 1, 1), (8, 7, 2, 1), (8, 0, 1, -1)):
            with self.assertRaises(ValueError):
                check.exact_dual(*args)
        with self.assertRaises(ValueError):
            check.explicit_coordinate_value(9, 0, 1, 1)

    def test_registered_selection_uses_exact_values_and_preserves_scope(self):
        rows = [check.dual_certificate(4, 1, 1, multiplier, F(1, 4), 8) for multiplier in (1, 3, 10)]
        selected = check.select_registered(rows)
        best = max(F(row["dual_lower_exact"]) for row in rows)
        self.assertEqual(F(selected["dual_lower_exact"]), best)
        self.assertIn(selected["multiplier"], (1, 3, 10))
        self.assertFalse(selected["globally_optimized_multiplier"])

    def test_protocol_freeze_rejects_types_expansion_and_duplicate_keys(self):
        for key, value in (("version", True), ("version", 1.0), ("multipliers", [1000000000]),
                           ("title", "changed"), ("maximum_integer_bits", 1)):
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
        for relative in ("experiments/check_finite_decision.py", "tests/test_finite_decision.py",
                         "experiments/finite_decision_protocol.json", "experiments/check_sharp_cost.py"):
            (root/relative).write_bytes((ROOT/relative).read_bytes())
        for name in ("finite-decision-theorem.md", "nonzero-minimax-theorem.md"):
            (root/"docs"/name).write_text("Temporary proof fixture.\n")
        return root, root/"experiments/finite_decision_protocol.json"

    def test_six_source_pins_bounded_snapshot_and_every_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root, path = self.fixture(directory)
            original_read = Path.read_bytes
            def bounded(candidate):
                if candidate == path:
                    self.fail("protocol must use a bounded stream")
                return original_read(candidate)
            with patch.object(check, "ROOT", root), \
                 patch.object(check, "__file__", str(root/"experiments/check_finite_decision.py")), \
                 patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                 patch.object(check, "calculate", return_value={"fixture": True}), \
                 patch.object(Path, "read_bytes", bounded):
                row = check.build_results(None, path)
            self.assertEqual(len(row["source_sha256"]), 6)
            self.assertEqual(row["protocol_sha256"], hashlib.sha256(original_read(path)).hexdigest())
            for relative in row["source_sha256"]:
                source = root/relative
                original = source.read_bytes()
                def mutate(_protocol):
                    source.write_bytes(original+b"\n")
                    return {}
                with patch.object(check, "ROOT", root), \
                     patch.object(check, "__file__", str(root/"experiments/check_finite_decision.py")), \
                     patch.object(check, "IMPORTED_HELPER_PATH", root/"experiments/check_sharp_cost.py"), \
                     patch.object(check, "calculate", side_effect=mutate):
                    with self.subTest(source=relative), self.assertRaisesRegex(RuntimeError, "changed"):
                        check.build_results(None, path)
                source.write_bytes(original)

    def test_overwrite_and_invalid_protocol_prevent_work_and_output_creation(self):
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

    def test_runtime_guards_survive_optimized_python(self):
        code = ("from unittest.mock import patch\nfrom experiments import check_finite_decision as c\n"
                "with patch.object(c, 'MAX_INTEGER_BITS', 4):\n    c.exact_dual(16,3,2,100)\n")
        result = subprocess.run([sys.executable, "-B", "-S", "-O", "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError", result.stderr)


if __name__ == "__main__":
    unittest.main()
