"""Integrity and exact-label tests for the standalone zero-only workflow."""

from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from goodhart_audit import zero


def pools():
    return [{"prompt_id": f"p{i:02}", "candidates": [
        {"candidate_id": "best", "proxy": 2., "text": "First candidate", "loss": 1},
        {"candidate_id": "other", "proxy": 1., "text": "Second candidate", "loss": 1},
    ]} for i in range(8)]


class ZeroWorkflowTests(unittest.TestCase):
    def selected_plan(self):
        with patch.object(zero.secrets, "randbits", return_value=0):
            plan = zero.make_zero_plan(pools(), [1, 2], "1/8", "1/4", "Exact toy loss")
        self.assertEqual(len(plan["queries"]), 16)
        return plan

    def test_score_only_plan_is_replayable_and_does_not_reveal_source_losses(self):
        plan = self.selected_plan()
        self.assertEqual(len(plan["random_tape_hex"]), 16)
        self.assertTrue(all(query["loss"] is None for query in plan["queries"]))
        self.assertTrue(all(isinstance(query["proxy"], str) for query in plan["queries"]))
        self.assertEqual(plan["queries"][0]["rank"], 1)
        changed = pools()
        for pool in changed:
            pool["candidates"].reverse()
            for candidate in pool["candidates"]:
                candidate["loss"] = Decimal("NaN")
        changed.reverse()
        with patch.object(zero.secrets, "randbits", return_value=0):
            replay = zero.make_zero_plan(changed, [2, 1], "0.125", "0.25", "Exact toy loss")
        self.assertEqual(replay, plan)

    def test_missing_zero_and_positive_states_and_external_commitment(self):
        plan = self.selected_plan()
        commitment = zero.plan_sha256(plan)
        self.assertEqual(len(commitment), 64)
        pending = zero.zero_report(pools(), plan, commitment)
        self.assertEqual(pending["status"], "pending")
        self.assertFalse(pending["certified"])
        plan["queries"][0]["loss"] = Decimal("1e-400")
        positive = zero.zero_report(pools(), plan, commitment)
        self.assertEqual(positive["status"], "not_certified")
        self.assertEqual(positive["remaining_query_count"], 15)
        for query in plan["queries"]:
            query["loss"] = 0
        complete = zero.zero_report(pools(), plan, commitment)
        self.assertEqual(complete["status"], "certified")
        self.assertEqual(complete["certified_budgets"], [1, 2])
        self.assertEqual(complete["observed_query_count"], 16)
        self.assertEqual(zero.plan_sha256(plan), commitment)

    def test_empty_selection_is_honest_and_not_redrawn(self):
        with patch.object(zero, "exact_randbelow", side_effect=lambda n, bits: n-1):
            plan = zero.make_zero_plan(pools(), [1, 2], "1/8", "1/4", "Exact toy loss")
        self.assertEqual(plan["queries"], [])
        report = zero.zero_report(pools(), plan, zero.plan_sha256(plan))
        self.assertEqual(report["status"], "certified")
        self.assertTrue(report["empty_selection"])
        self.assertEqual(report["observed_query_count"], 0)
        self.assertGreater(Fraction(report["expected_zero_table_labels"]), 0)

    def test_changed_metadata_tape_queries_pool_and_commitment_are_rejected(self):
        plan = self.selected_plan()
        commitment = zero.plan_sha256(plan)
        variants = []
        for key, value in [("rubric", "Changed rubric"), ("threshold", "1/10"),
                           ("delta", "1/20"), ("budgets", [1])]:
            variant = deepcopy(plan)
            variant[key] = value
            variants.append(variant)
        variant = deepcopy(plan)
        variant["random_tape_hex"][0] = "1"
        variants.append(variant)
        variant = deepcopy(plan)
        variant["queries"][0]["text"] = "Changed text"
        variants.append(variant)
        variant = deepcopy(plan)
        variant["queries"].reverse()
        variants.append(variant)
        variant = deepcopy(plan)
        del variant["queries"][0]["loss"]
        variants.append(variant)
        for variant in variants:
            with self.assertRaises(ValueError):
                zero.zero_report(pools(), variant, commitment)
        changed_pool = pools()
        changed_pool[0]["candidates"][0]["proxy"] = 4
        with self.assertRaises(ValueError):
            zero.zero_report(changed_pool, plan, commitment)
        for invalid in [None, "", "0"*64, 7, True]:
            with self.assertRaises(ValueError):
                zero.zero_report(pools(), plan, invalid)

    def test_committed_but_invalid_tape_and_query_list_cannot_be_reported(self):
        plan = self.selected_plan()
        for mutate in [lambda p: p["random_tape_hex"].__setitem__(0, "f"*1000),
                       lambda p: p["random_tape_hex"].pop(),
                       lambda p: p["queries"].pop(),
                       lambda p: p["queries"][0].__setitem__("rank", 2),
                       lambda p: p["design"].__setitem__("cost_factor", 1)]:
            changed = deepcopy(plan)
            mutate(changed)
            with self.assertRaises(ValueError):
                zero.zero_report(pools(), changed, zero.plan_sha256(changed))

    def test_labels_reject_booleans_nonfinite_out_of_range_and_float_inputs(self):
        plan = self.selected_plan()
        commitment = zero.plan_sha256(plan)
        for label in [True, False, Decimal("NaN"), Decimal("Infinity"), Decimal("-1e-400"),
                      Decimal("1.00000000000000000000001"), -1, 2, 0.0, "0"]:
            plan["queries"][0]["loss"] = label
            with self.subTest(label=label), self.assertRaises(ValueError):
                zero.zero_report(pools(), plan, commitment)

    def test_annotation_reader_preserves_tiny_positive_and_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"plan.json"
            path.write_text('{"queries":[{"loss":1e-400}]}')
            self.assertEqual(zero.read_plan(path)["queries"][0]["loss"], Decimal("1e-400"))
            for content in ['{"queries":[],"queries":[]}', '{"queries":[{"loss":0,"loss":1}]}',
                            '{"queries":[{"loss":NaN}]}', '{"queries":[{"loss":Infinity}]}']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    zero.read_plan(path)

    def test_input_and_resource_limits_fail_before_random_draws(self):
        invalid = [([], [1], "1/8", "1/4", "rule"),
                   (pools(), [1, 2], "1/2", "1/4", "rule"),
                   (pools(), [1, 2], "1/8", "1/2", "rule"),
                   (pools(), [1, 2], "1/8", "1/4", ""),
                   (pools(), [True], "1/8", "1/4", "rule"),
                   (pools(), [1, 1], "1/8", "1/4", "rule")]
        excessive = [{"prompt_id": "p", "candidates": [{"candidate_id": str(i), "proxy": i}
                                                            for i in range(1025)]}]
        invalid.append((excessive, [1], "1/8", "1/4", "rule"))
        with patch.object(zero.secrets, "randbits", side_effect=AssertionError("randomness used for invalid input")):
            for arguments in invalid:
                with self.subTest(arguments=arguments[1:]), self.assertRaises(ValueError):
                    zero.make_zero_plan(*arguments)

    def test_output_size_limit_is_checked_before_subset_randomness(self):
        calls = []
        def bits(width):
            calls.append(width)
            return 0
        with patch.object(zero, "MAX_JSON_BYTES", 4000), patch.object(zero.secrets, "randbits", side_effect=bits):
            with self.assertRaises(ValueError):
                zero.make_zero_plan(pools(), [1, 2], "1/8", "1/4", "Exact toy loss")
        self.assertEqual(calls, [])

    def test_aggregate_pool_limit_precedes_fingerprint_and_design_expansion(self):
        source = pools()
        for pool in source:
            for candidate in pool["candidates"]:
                candidate["text"] = "x"*300
        with patch.object(zero, "MAX_JSON_BYTES", 4000), \
             patch.object(zero, "pool_fingerprint", side_effect=AssertionError("unbounded fingerprint reached")), \
             patch.object(zero, "design_probabilities", side_effect=AssertionError("design expansion reached")):
            with self.assertRaisesRegex(ValueError, "JSON exceeds"):
                zero.make_zero_plan(source, [1, 2], "1/8", "1/4", "Exact toy loss")

    def test_empty_candidate_text_is_valid_and_committed(self):
        source = [{"prompt_id": "p", "candidates": [
            {"candidate_id": "c", "proxy": 1, "text": ""}]}]
        plan = zero.make_zero_plan(source, [1], "1/8", "1/4", "Zero loss")
        self.assertEqual(plan["queries"][0]["text"], "")
        plan["queries"][0]["loss"] = 0
        self.assertEqual(zero.zero_report(source, plan, zero.plan_sha256(plan))["status"], "certified")

    def test_cli_without_site_packages_preserves_exact_labels_and_outputs(self):
        repo = Path(__file__).resolve().parents[1]
        def run(*arguments):
            return subprocess.run([sys.executable, "-B", "-S", "-m", "goodhart_audit.zero", *map(str, arguments)],
                                  cwd=repo, capture_output=True, text=True, timeout=30)
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            pool_path, plan_path = directory/"pool.jsonl", directory/"plan.json"
            pool_path.write_text(json.dumps({"prompt_id": "p", "candidates": [
                {"candidate_id": "c", "proxy": 1, "text": "A candidate", "loss": 1}]})+"\n")
            arguments = ["plan", "--pool", pool_path, "--out", plan_path,
                         "--budgets", "1", "--threshold", "1/8", "--delta", "1/4", "--rubric", "Toy"]
            planned = run(*arguments)
            self.assertEqual(planned.returncode, 0, planned.stderr)
            commitment = planned.stdout.strip()
            self.assertRegex(commitment, r"^[0-9a-f]{64}$")
            original = plan_path.read_bytes()
            plan = json.loads(original)
            self.assertEqual(len(plan["queries"]), 1)
            self.assertIsNone(plan["queries"][0]["loss"])
            overwrite = run(*arguments)
            self.assertNotEqual(overwrite.returncode, 0)
            self.assertEqual(plan_path.read_bytes(), original)
            self.assertNotEqual(run(*arguments, "--seed", "17").returncode, 0)
            report_args = ["report", "--pool", pool_path, "--plan", plan_path,
                           "--plan-sha256", commitment]
            for label, status in [("null", "pending"), ("1e-400", "not_certified"), ("0.0", "certified")]:
                plan_path.write_text(original.decode().replace('"loss": null', '"loss": '+label))
                output = directory/(status+".json")
                reported = run(*report_args, "--out", output)
                self.assertEqual(reported.returncode, 0, reported.stderr)
                self.assertEqual(reported.stdout.strip(), status)
                self.assertEqual(json.loads(output.read_text())["status"], status)
                saved = output.read_bytes()
                self.assertNotEqual(run(*report_args, "--out", output).returncode, 0)
                self.assertEqual(output.read_bytes(), saved)
            invalid_output = directory/"invalid.json"
            plan_path.write_text(original.decode().replace('"loss": null', '"loss": 0, "loss": 1'))
            self.assertNotEqual(run(*report_args, "--out", invalid_output).returncode, 0)
            self.assertFalse(invalid_output.exists())


if __name__ == "__main__":
    unittest.main()
