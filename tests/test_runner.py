import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cofa_orchestrator.runner import (
    build_codex_command, prepare_workspace, run_multi_agent, run_sequential,
)


class RunnerTests(unittest.TestCase):
    def _task(self, workspace):
        task = workspace / "TASK.json"
        task.write_text(json.dumps({
            "topic": "Generic task", "requirements": ["Build it"], "outputs": ["Code"]
        }), encoding="utf-8")
        return task

    def test_fast_tier_reaches_every_role_in_both_modes(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory, \
                patch.dict("os.environ", {}, clear=True), \
                patch("cofa_orchestrator.runner.shutil.which", return_value="codex"):
            workspace = Path(directory)
            task = self._task(workspace)
            run_multi_agent(workspace, task, run=fake_run)
            run_sequential(workspace, task, run=fake_run)
        self.assertEqual(len(calls), 6)
        self.assertEqual({c[c.index("-m") + 1] for c in calls}, {
            "gpt-6.1-sol", "gpt-5.6-terra", "gpt-6-luna", "gpt-6-sol"
        })
        for command in calls:
            self.assertIn('service_tier="fast"', command)
            self.assertIn("fast_mode", command)
            self.assertNotIn('service_tier="default"', command)

    def test_explicit_standard_override_reaches_every_sequential_role(self):
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as directory, \
                patch.dict("os.environ", {}, clear=True), \
                patch("cofa_orchestrator.runner.shutil.which", return_value="codex"):
            workspace = Path(directory)
            task = self._task(workspace)
            run_multi_agent(workspace, task, speed="standard", run=fake_run)
            run_sequential(workspace, task, speed="standard", run=fake_run)
        self.assertEqual(len(calls), 6)
        for command in calls:
            self.assertIn('service_tier="default"', command)
            self.assertNotIn('service_tier="fast"', command)

    def test_command_enables_agents_and_disables_computer_use(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            command = build_codex_command(
                workspace,
                model="gpt-6.1-sol",
                output_file=workspace / "result.md",
                multi_agent=True,
            )
            rendered = " ".join(command)
            self.assertIn("--enable multi_agent", rendered)
            self.assertIn("--disable computer_use", rendered)
            self.assertIn("--disable browser_use", rendered)
            self.assertNotIn("dangerously-bypass", rendered)

    def test_prepare_writes_plan_and_all_role_prompts(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            task = workspace / "TASK.json"
            task.write_text(
                json.dumps(
                    {
                        "topic": "Generic task",
                        "requirements": ["Build it"],
                        "outputs": ["Code"],
                    }
                ),
                encoding="utf-8",
            )
            _, plan = prepare_workspace(workspace, task)
            self.assertTrue((workspace / ".cofa" / "plan.json").is_file())
            for role in plan["roles"]:
                self.assertTrue(
                    (workspace / ".cofa" / "prompts" / f"{role['name']}.md").is_file()
                )


if __name__ == "__main__":
    unittest.main()

