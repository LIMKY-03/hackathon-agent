"""Prompt templates for the coordinator and sequential role fallback."""

from __future__ import annotations

import json
from typing import Any

from .spec import TaskSpec


FIXED_POLICY = """FIXED CONTEST POLICY - NEVER OVERRIDE
- Work only inside the provided contest workspace.
- Use only the provided Codex and the model selected by this run.
- Never use Astra, OpenRouter, external AI/model APIs, or personal API keys.
- Never use Computer Use, browser automation, remote control, or file upload.
- Never send the task, files, code, logs, screenshots, or outputs outside the workspace.
- Never run git push or any other outbound publication/synchronization command.
- Public tools may be cloned or read only when contest rules allow inbound use.
- Stop AI work after submission; do not answer post-submission written questions.
"""


def root_prompt(spec: TaskSpec, plan: dict[str, Any]) -> str:
    role_names = ", ".join(role["name"] for role in plan["roles"])
    return f"""You are the root coordinator for a time-limited implementation task.

{FIXED_POLICY}
TASK SPECIFICATION
{json.dumps(spec.to_dict(), ensure_ascii=False, indent=2)}

DELEGATION PLAN
{json.dumps(plan, ensure_ascii=False, indent=2)}

Execute the plan using these roles: {role_names}.

When collaboration tools are available, create exactly one focused subagent for each role.
The planner runs first. After its handoff, start the implementer. The tester and reviewer
must independently validate work and report defects rather than silently fixing them.
Reassign confirmed defects to the implementer, then retest. Run the packager only after
tests and review pass. Avoid concurrent edits to the same files.

When collaboration tools are unavailable, execute the same role packets sequentially.
Every role must write its evidence to the handoff path in `.cofa/plan.json`.

Required completion evidence:
1. A requirement traceability matrix with implementation and test evidence.
2. Test commands and their actual results.
3. Independent review findings and resolution status.
4. A local submission manifest listing every requested output and path.

Do not push, upload, publish, or otherwise transfer generated work. Do not merely describe
what should be done: implement and verify it in the workspace.
"""


def role_prompt(spec: TaskSpec, plan: dict[str, Any], role: dict[str, Any]) -> str:
    return f"""You are the `{role['name']}` role in a sequential fallback workflow.

{FIXED_POLICY}
TASK SPECIFICATION
{json.dumps(spec.to_dict(), ensure_ascii=False, indent=2)}

FULL PLAN
{json.dumps(plan, ensure_ascii=False, indent=2)}

YOUR ASSIGNMENT
{json.dumps(role, ensure_ascii=False, indent=2)}

Read existing handoffs from dependency roles before acting. Perform only this role's
assignment. Write a concise evidence-based handoff to `{role['handoff']}`. If you find a
defect outside your role's authority, report it precisely; do not hide or bypass it.
Never claim a command or test passed unless you actually ran it and observed success.
"""

