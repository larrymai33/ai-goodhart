"""Exact arithmetic regressions for the standalone zero-cost checker."""

from fractions import Fraction as F
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import check_zero_cost as check


class ZeroCostTests(unittest.TestCase):
    @staticmethod
    def small_protocol():
        protocol = json.loads((check.ROOT/"experiments/zero_cost_protocol.json").read_text())
        protocol.update({"block_check_max_pool_size": 1, "block_family_types": ["full"],
                         "hypergeometric_check_max_block_size": 1,
                         "risk_thresholds": ["1/8"], "error_probabilities": ["1/4"],
                         "cost_cases": [{"name": "one", "prompts": 1, "pool_size": 1,
                                         "max_budget": 1, "family": "full", "tau": "1/8", "delta": "1/4"}],
                         "high_threshold_pool_sizes": [2]})
        return protocol

    def test_optimized_python_cannot_emit_an_unchecked_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = Path(directory)/"protocol.json"
            protocol.write_text(json.dumps(self.small_protocol()))
            output = Path(directory)/"unchecked.json"
            completed = subprocess.run([sys.executable, "-O", "-B", "-S", "-m", "experiments.check_zero_cost",
                                        "--protocol", str(protocol), "--out", str(output)],
                                       cwd=check.ROOT, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertNotIn("Passed", completed.stdout)

    def test_supplied_theorem_claims_must_match_the_checked_theorem(self):
        original = self.small_protocol()
        variants = []
        for field, replacement in [("factor", 1), ("factor", 160.0),
                                   ("maximum_risk_threshold", "1"),
                                   ("maximum_error_probability", "1/2"),
                                   ("budget_family_requirement", "Any sparse grid"),
                                   ("objective", "Expected queries on every loss table"),
                                   ("decision", "Certify any selected target"),
                                   ("comparator", "Only fixed sampling designs")]:
            variants.append((field, {**original, "theorem": {**original["theorem"], field: replacement}}))
        for field in ("factor", "maximum_risk_threshold", "maximum_error_probability"):
            theorem = {key: value for key, value in original["theorem"].items() if key != field}
            variants.append(("missing_"+field, {**original, "theorem": theorem}))
        variants.append(("missing_theorem", {key: value for key, value in original.items() if key != "theorem"}))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"protocol.json"
            path.write_text(json.dumps(original))
            self.assertEqual(check.build_results(original, path)["protocol"]["theorem"], original["theorem"])
            for name, protocol in variants:
                path.write_text(json.dumps(protocol))
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "theorem"):
                    check.build_results(protocol, path)

    def test_protocol_mutation_after_initial_read_is_rejected(self):
        protocol = self.small_protocol()
        with tempfile.TemporaryDirectory() as directory:
            path = (Path(directory)/"protocol.json").resolve()
            path.write_text(json.dumps(protocol))
            original_text, original_bytes = Path.read_text, Path.read_bytes
            mutated = False

            def mutate_after_read(source, value):
                nonlocal mutated
                if source == path and not mutated:
                    mutated = True
                    path.write_text(json.dumps({**protocol, "race_marker": "changed after snapshot"}))
                return value

            def read_text(source, *args, **kwargs):
                return mutate_after_read(source, original_text(source, *args, **kwargs))

            def read_bytes(source):
                return mutate_after_read(source, original_bytes(source))

            # The same first-read mutation applies whether production captures
            # text or bytes; only an initial shared parse/hash snapshot is safe.
            with patch.object(Path, "read_text", read_text), patch.object(Path, "read_bytes", read_bytes):
                with self.assertRaisesRegex(RuntimeError, "changed during"):
                    check.build_results(protocol, path)
            self.assertTrue(mutated)

    def test_rank_law_matches_enumerated_winner_counts(self):
        for m in range(1, 8):
            for n in range(1, m+1):
                counts = [0]*m
                subsets = list(itertools.combinations(range(m), n))
                for subset in subsets:
                    counts[min(subset)] += 1
                self.assertEqual(check.exact_weights(m, n), tuple(F(count, len(subsets)) for count in counts))

    def test_fourfold_blocks_cover_rounding_and_last_block_boundaries(self):
        budgets = check.budget_family(19, 16, "powers_four_plus_max")
        self.assertEqual(budgets, (1, 4, 16))
        blocks = check.rank_blocks(19, budgets)
        self.assertEqual([(b["budget"], b["first_rank"], b["last_rank"]) for b in blocks],
                         [(1, 5, 19), (4, 2, 4), (16, 1, 1)])
        for m in range(1, 21):
            for n in range(1, m+1):
                for kind in ("full", "powers_four_plus_max", "dyadic_plus_max"):
                    family = check.budget_family(m, n, kind)
                    rows = {budget: check.exact_weights(m, budget) for budget in family}
                    covered = []
                    for block in check.rank_blocks(m, family):
                        ranks = range(block["first_rank"], block["last_rank"]+1)
                        covered.extend(ranks)
                        size = len(ranks)
                        for rank in ranks:
                            self.assertGreater(size*rows[block["budget"]][rank-1], F(1, 4))
                            self.assertLessEqual(size*max(row[rank-1] for row in rows.values()), 4)
                    self.assertEqual(sorted(covered), list(range(1, m+1)))

    def test_arbitrary_sparse_family_and_invalid_sizes_are_rejected(self):
        for m, family in [(8, (1, 8)), (8, (4, 8)), (8, (1, 4, 9)), (0, (1,)), (True, (1,))]:
            with self.subTest(m=m, family=family), self.assertRaises(ValueError):
                check.rank_blocks(m, family)

    def test_hypergeometric_miss_and_fractional_inverse_match_hand_values(self):
        self.assertEqual([check.hypergeometric_miss(4, 2, d) for d in range(5)],
                         [F(1), F(1, 2), F(1, 6), F(0), F(0)])
        self.assertEqual(check.inverse_miss_bound(4, 2, F(1, 4)), F(7, 4))
        self.assertEqual(check.inverse_miss_bound(4, 2, F(1, 6)), F(2))
        self.assertEqual(check.inverse_miss_bound(4, 1, F(1, 4)), F(3))

    def test_log_certificate_and_odd_taylor_are_conservative(self):
        certificate = check.log_upper_certificate(F(1, 20))
        self.assertEqual(certificate["bound"], 3)
        self.assertGreaterEqual(certificate["partial_sum"], 20)
        self.assertEqual(check.inclusion_upper(F(0)), 0)
        self.assertEqual(check.inclusion_upper(F(1)), F(19, 30))
        self.assertEqual(check.inclusion_upper(F(2)), F(14, 15))
        self.assertEqual(check.inclusion_upper(F(3)), 1)

    def test_single_item_cost_certificate_has_known_bounds(self):
        row = check.cost_certificate({"name": "one", "prompts": 1, "pool_size": 1,
                                      "max_budget": 1, "family": "full", "tau": "1/8", "delta": "1/4"})
        self.assertEqual(F(row["lower"]), F(3, 4))
        self.assertEqual(F(row["upper"]), 1)
        self.assertEqual(len(row["blocks"]), 1)

    def test_boundary_failure_count_is_strictly_unsafe_not_equal_to_threshold(self):
        row = check.cost_certificate({"name": "boundary", "prompts": 1, "pool_size": 8,
                                      "max_budget": 8, "family": "full", "tau": "1/8", "delta": "1/4"})
        bottom = row["blocks"][0]
        self.assertEqual(F(bottom["minimum_target_mass"]), F(1, 8))
        self.assertEqual(bottom["unsafe_subset_size"], 2)

    def test_invalid_cost_geometries_and_outside_theorem_parameters_fail(self):
        base = {"name": "test", "prompts": 1, "pool_size": 8, "max_budget": 8,
                "family": "full", "tau": "1/8", "delta": "1/4"}
        for key, value in [("prompts", 0), ("prompts", True), ("pool_size", 0),
                           ("max_budget", 9), ("family", "arbitrary"), ("tau", "1/2"),
                           ("tau", "0"), ("delta", "1/2"), ("delta", "nan")]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                check.cost_certificate({**base, key: value})

    def test_empty_check_grid_is_not_reported_as_success(self):
        with self.assertRaises(ValueError):
            check.check_hypergeometric(8, [], [F(1, 4)])

    def test_existing_artifact_is_preserved_by_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"existing.json"
            path.write_bytes(b"preserve this evidence")
            completed = subprocess.run([sys.executable, "-B", "-S", "-m", "experiments.check_zero_cost",
                                        "--out", str(path)], cwd=check.ROOT, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(path.read_bytes(), b"preserve this evidence")

    def test_supplied_protocol_cannot_disagree_with_pinned_protocol_file(self):
        protocol = self.small_protocol()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"protocol.json"
            path.write_text(json.dumps(protocol))
            with self.assertRaisesRegex(ValueError, "protocol file"):
                check.build_results({**protocol, "changed": True}, path)

    def test_high_threshold_counterexample_detects_only_top_containing_sets(self):
        for m in range(2, 9):
            row = check.high_threshold_case(m, F(1, 4))
            self.assertTrue(row["binary_unsafe_iff_contains_top_rank"])
            self.assertEqual(F(row["optimal_cost"]), F(3, 4))
            weights = [check.exact_weights(m, n) for n in range(1, m+1)]
            tau = 1-F(1, 2*m)
            for mask in range(1 << m):
                unsafe = any(sum((w[i] for i in range(m) if mask >> i & 1), F(0)) > tau for w in weights)
                self.assertEqual(unsafe, bool(mask & 1))
            self.assertGreaterEqual(F(row["competitive_ratio_lower"]), 1)

    def test_convexity_and_rounding_checker_exercises_small_boundaries(self):
        report = check.check_hypergeometric(32, [F(1, 8), F(1, 100)], [F(1, 4), F(1, 20)])
        self.assertGreater(report["convexity_checks"], 100)


if __name__ == "__main__":
    unittest.main()
