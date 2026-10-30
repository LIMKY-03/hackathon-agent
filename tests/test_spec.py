import json
import tempfile
import unittest
from pathlib import Path

from cofa_orchestrator.spec import SpecError, TaskSpec


VALID = {
    "schema_version": 1,
    "topic": "Generic task",
    "requirements": ["Build the feature"],
    "outputs": ["Working code"],
    "time_budget_minutes": 180,
}


class SpecTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TASK.json"
            original = TaskSpec.from_dict(VALID)
            original.save(path)
            self.assertEqual(TaskSpec.load(path), original)

    def test_missing_outputs_are_rejected(self):
        invalid = dict(VALID)
        invalid["outputs"] = []
        with self.assertRaises(SpecError):
            TaskSpec.from_dict(invalid)

    def test_budget_above_contest_window_is_rejected(self):
        invalid = dict(VALID)
        invalid["time_budget_minutes"] = 181
        with self.assertRaises(SpecError):
            TaskSpec.from_dict(invalid)

    def test_invalid_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "TASK.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(SpecError):
                TaskSpec.load(path)


if __name__ == "__main__":
    unittest.main()

