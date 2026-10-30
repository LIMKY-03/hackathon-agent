import tempfile
import unittest
from pathlib import Path

from cofa_orchestrator.cli import main


class CliTests(unittest.TestCase):
    def test_init_and_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            rc = main(
                [
                    "init",
                    "--workspace",
                    str(workspace),
                    "--topic",
                    "Generic task",
                    "--requirement",
                    "Build it",
                    "--output",
                    "Working code",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(
                main(["plan", "--workspace", str(workspace), "--profile", "balanced"]),
                0,
            )
            self.assertTrue((workspace / ".cofa" / "plan.json").exists())


if __name__ == "__main__":
    unittest.main()

