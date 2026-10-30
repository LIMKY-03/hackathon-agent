import json
import tempfile
import unittest
from pathlib import Path

from cofa_orchestrator.runner import build_codex_command, prepare_workspace


class RunnerTests(unittest.TestCase):
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

