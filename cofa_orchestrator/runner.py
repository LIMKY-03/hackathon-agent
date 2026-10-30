"""Workspace preparation and safe Codex CLI execution."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from .planner import build_plan
from .policy import (
    assert_no_external_ai_credentials,
    assert_not_post_submission,
    canonical_model,
    codex_safety_feature_args,
)
from .spec import TaskSpec
from .templates import role_prompt, root_prompt


@dataclass(frozen=True)
class RunResult:
    returncode: int
    command: tuple[str, ...]
    output_file: Path


def prepare_workspace(
    workspace: Path,
    task_path: Path,
    *,
    profile: str = "balanced",
    single_model: str | None = None,
) -> tuple[TaskSpec, dict[str, Any]]:
    workspace = workspace.resolve()
    assert_not_post_submission(workspace)
    spec = TaskSpec.load(task_path.resolve())
    plan = build_plan(spec, profile=profile, single_model=single_model)

    cofa_dir = workspace / ".cofa"
    prompts_dir = cofa_dir / "prompts"
    handoffs_dir = cofa_dir / "handoffs"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    handoffs_dir.mkdir(parents=True, exist_ok=True)

    (cofa_dir / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (prompts_dir / "root.md").write_text(root_prompt(spec, plan), encoding="utf-8")
    for role in plan["roles"]:
        (prompts_dir / f"{role['name']}.md").write_text(
            role_prompt(spec, plan, role), encoding="utf-8"
        )
    return spec, plan


def build_codex_command(
    workspace: Path,
    *,
    model: str,
    output_file: Path,
    multi_agent: bool,
) -> list[str]:
    command = [
        "codex",
        "exec",
        "-C",
        str(workspace.resolve()),
        "-m",
        canonical_model(model),
        "-s",
        "workspace-write",
        "-a",
        "never",
        "--skip-git-repo-check",
        "--output-last-message",
        str(output_file.resolve()),
    ]
    command.extend(codex_safety_feature_args())
    command.extend(["--enable" if multi_agent else "--disable", "multi_agent"])
    command.append("-")
    return command


def _execute(
    command: Sequence[str],
    prompt: str,
    *,
    workspace: Path,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    completed = run(
        list(command),
        input=prompt,
        text=True,
        cwd=workspace,
        check=False,
    )
    return completed.returncode


def run_multi_agent(
    workspace: Path,
    task_path: Path,
    *,
    model: str = "gpt-6.1-sol",
    profile: str = "balanced",
    dry_run: bool = False,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> RunResult:
    workspace = workspace.resolve()
    assert_not_post_submission(workspace)
    assert_no_external_ai_credentials()
    if not dry_run and shutil.which("codex") is None:
        raise RuntimeError("Codex CLI was not found on PATH.")
    prepare_workspace(workspace, task_path, profile=profile)
    prompt_path = workspace / ".cofa" / "prompts" / "root.md"
    output_file = workspace / ".cofa" / "root-result.md"
    command = build_codex_command(
        workspace,
        model=model,
        output_file=output_file,
        multi_agent=True,
    )
    returncode = 0 if dry_run else _execute(
        command, prompt_path.read_text(encoding="utf-8"), workspace=workspace, run=run
    )
    return RunResult(returncode, tuple(command), output_file)


def run_sequential(
    workspace: Path,
    task_path: Path,
    *,
    profile: str = "balanced",
    single_model: str | None = None,
    dry_run: bool = False,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[RunResult]:
    workspace = workspace.resolve()
    assert_not_post_submission(workspace)
    assert_no_external_ai_credentials()
    if not dry_run and shutil.which("codex") is None:
        raise RuntimeError("Codex CLI was not found on PATH.")
    _, plan = prepare_workspace(
        workspace, task_path, profile=profile, single_model=single_model
    )
    results: list[RunResult] = []
    for role in plan["roles"]:
        prompt_path = workspace / ".cofa" / "prompts" / f"{role['name']}.md"
        output_file = workspace / ".cofa" / f"{role['name']}-result.md"
        command = build_codex_command(
            workspace,
            model=role["suggested_model"],
            output_file=output_file,
            multi_agent=False,
        )
        returncode = 0 if dry_run else _execute(
            command, prompt_path.read_text(encoding="utf-8"), workspace=workspace, run=run
        )
        result = RunResult(returncode, tuple(command), output_file)
        results.append(result)
        if returncode != 0:
            break
    return results

