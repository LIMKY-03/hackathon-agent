import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cofa_orchestrator.cli import main


class CliTests(unittest.TestCase):
    def test_validate_status_and_dry_runs_allow_platform_credentials(self):
        credentials = {
            "OPENAI_API_KEY": "test-platform-sentinel",
            "GOOGLE_API_KEY": "test-maps-sentinel",
        }
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict("os.environ", credentials, clear=True):
            workspace = Path(directory)
            (workspace / "TASK.json").write_text(json.dumps({
                "topic": "Generic task", "requirements": ["Build it"], "outputs": ["Code"]
            }), encoding="utf-8")
            for command in [
                ["validate"],
                ["status"],
                ["run", "--mode", "multi-agent", "--dry-run"],
                ["run", "--mode", "sequential", "--dry-run"],
            ]:
                with self.subTest(command=command):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        rc = main(command + ["--workspace", str(workspace)])
                    self.assertEqual(rc, 0)
                    output = stdout.getvalue() + stderr.getvalue()
                    for name, value in credentials.items():
                        self.assertNotIn(name, output)
                        self.assertNotIn(value, output)
                    self.assertNotIn("External/personal AI credential variables are set:", output)
                    if command == ["status"]:
                        self.assertIsNotNone(json.loads(stdout.getvalue())["credential_environment_notice"])

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

