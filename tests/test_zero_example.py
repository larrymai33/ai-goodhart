import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from examples import annotate_zero_example


ROOT = Path(__file__).resolve().parents[1]
ANNOTATOR = ROOT / "examples" / "annotate_zero_example.py"


class ZeroExampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / "plan.json"
        self.output = self.directory / "annotated.json"

    def plan(self, texts):
        return {
            "plan_sha256": "a" * 64,
            "rubric": "Exact integer addition; 0 correct, 1 incorrect.",
            "random_tape": ["0", "abc", "123456789abcdef"],
            "design": {"threshold": "1/10", "expected_cost": "123/7"},
            "unselected_metadata": {"identities": ["keep-this"], "count": 32},
            "queries": [
                {"prompt_id": "p", "candidate_id": str(i),
                 "text": text, "proxy": str(4 - i), "loss": None}
                for i, text in enumerate(texts)
            ],
        }

    def invoke(self, plan=None, raw=None):
        self.source.write_text(raw if raw is not None else json.dumps(plan),
                               encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-S", str(ANNOTATOR), "--plan", str(self.source),
             "--out", str(self.output)],
            cwd=ROOT, capture_output=True, text=True,
        )

    def test_cli_labels_integer_equations_and_preserves_every_other_value(self):
        plan = self.plan([
            "2 + 3 = 5", "2 + 3 = 6", "-3 + -4 = -7",
            "+0 + -0 = 0", "99999999999999999999 + 1 = 100000000000000000000",
        ])
        expected = copy.deepcopy(plan)
        for query, loss in zip(expected["queries"], [0, 1, 0, 0, 0]):
            query["loss"] = loss
        result = self.invoke(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), expected)
        self.assertEqual(self.source.read_text(encoding="utf-8"), json.dumps(plan))

    def test_malformed_equations_abort_without_creating_output(self):
        for text in ["2+3=5", "2 + 3 = 5\n", "2 + 3 = 5; print(1)",
                     "2.0 + 3 = 5", "2 + 3 = __import__('os')", "٢ + 3 = 5",
                     "9" * 101 + " + 1 = 0", None]:
            with self.subTest(text=text):
                result = self.invoke(self.plan(["1 + 1 = 2", text]))
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())

    def test_existing_output_and_preexisting_labels_are_not_overwritten(self):
        self.output.write_text("original evidence", encoding="utf-8")
        result = self.invoke(self.plan(["1 + 1 = 2"]))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "original evidence")
        self.output.unlink()
        plan = self.plan(["1 + 1 = 2"])
        plan["queries"][0]["loss"] = 1
        result = self.invoke(plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_duplicate_keys_and_noninteger_json_numbers_are_rejected(self):
        for raw in [
            '{"queries": [], "queries": []}',
            '{"queries": [{"text":"1 + 1 = 2", "loss":null, "loss":0}]}',
            '{"queries": [], "metadata": 1e-400}',
            '{"queries": [], "metadata": NaN}',
        ]:
            with self.subTest(raw=raw):
                self.output.unlink(missing_ok=True)
                result = self.invoke(raw=raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())

    def test_empty_selection_is_preserved(self):
        plan = self.plan([])
        result = self.invoke(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), plan)

    def test_output_size_expansion_fails_before_file_creation(self):
        for note in ("", "é" * 20):
            with self.subTest(note=note):
                self.output.unlink(missing_ok=True)
                plan = {"queries": [{"text": "1 + 1 = 2", "loss": None}], "note": note}
                raw = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
                self.source.write_text(raw, encoding="utf-8")
                small_limit = len(raw.encode("utf-8")) + 1
                arguments = [str(ANNOTATOR), "--plan", str(self.source), "--out", str(self.output)]
                with patch.object(annotate_zero_example, "MAX_JSON_BYTES", small_limit, create=True), \
                        patch.object(sys, "argv", arguments), \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
                    with self.assertRaises(SystemExit) as raised:
                        annotate_zero_example.main()
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("output", errors.getvalue())
                self.assertFalse(self.output.exists())
                self.assertEqual(self.source.read_text(encoding="utf-8"), raw)


if __name__ == "__main__":
    unittest.main()
