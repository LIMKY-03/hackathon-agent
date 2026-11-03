"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .planner import MODEL_PROFILES
from .policy import (
    ALLOWED_MODELS,
    PolicyViolation,
    assert_no_external_ai_credentials,
    assert_not_post_submission,
    canonical_model,
    create_post_submission_lock,
    lock_path,
)
from .runner import prepare_workspace, run_multi_agent, run_sequential
from .spec import SpecError, TaskSpec


def _workspace(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Workspace is not a directory: {path}")
    return path


def _task_path(args: argparse.Namespace) -> Path:
    path = Path(args.task).expanduser()
    return path.resolve() if path.is_absolute() else (args.workspace / path).resolve()


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", type=_workspace, default=Path.cwd().resolve())
    parser.add_argument("--task", default="TASK.json", help="Task JSON path")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cofa-orchestrator",
        description="Policy-aware orchestration for the contest-provided Codex CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a task specification inside the workspace")
    _add_common(init)
    init.add_argument("--topic")
    init.add_argument("--context", default="")
    init.add_argument("--requirement", action="append", default=[])
    init.add_argument("--constraint", action="append", default=[])
    init.add_argument("--output", action="append", default=[])
    init.add_argument("--acceptance", action="append", default=[])
    init.add_argument("--time-budget", type=int, default=180)

    validate = sub.add_parser("validate", help="Validate task and execution policy")
    _add_common(validate)

    plan = sub.add_parser("plan", help="Create role packets and traceability plan")
    _add_common(plan)
    plan.add_argument("--profile", choices=MODEL_PROFILES, default="balanced")
    plan.add_argument("--model", choices=ALLOWED_MODELS)

    run = sub.add_parser("run", help="Run Codex orchestration")
    _add_common(run)
    run.add_argument("--mode", choices=("multi-agent", "sequential"), default="multi-agent")
    run.add_argument("--profile", choices=MODEL_PROFILES, default="balanced")
    run.add_argument("--model", choices=ALLOWED_MODELS)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument(
        "--speed", choices=("fast", "standard"), default="fast",
        help="Codex service speed for every role (default: fast).",
    )

    lock = sub.add_parser("lock", help="Permanently stop AI work after submission")
    lock.add_argument("--workspace", type=_workspace, default=Path.cwd().resolve())

    status = sub.add_parser("status", help="Show local orchestration status")
    status.add_argument("--workspace", type=_workspace, default=Path.cwd().resolve())
    return parser


def _init(args: argparse.Namespace) -> int:
    task = _task_path(args)
    if task.exists():
        raise SpecError(f"Refusing to overwrite existing task file: {task}")
    topic = args.topic or input("Topic: ").strip()
    requirements = args.requirement or [input("Primary requirement: ").strip()]
    outputs = args.output or [input("Primary output: ").strip()]
    spec = TaskSpec.from_dict(
        {
            "schema_version": 1,
            "topic": topic,
            "context": args.context,
            "requirements": requirements,
            "constraints": args.constraint,
            "outputs": outputs,
            "acceptance_criteria": args.acceptance,
            "time_budget_minutes": args.time_budget,
        }
    )
    spec.save(task)
    print(f"Created local task specification: {task}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    assert_not_post_submission(args.workspace)
    assert_no_external_ai_credentials()
    spec = TaskSpec.load(_task_path(args))
    print(
        json.dumps(
            {
                "valid": True,
                "topic": spec.topic,
                "requirements": len(spec.requirements),
                "outputs": len(spec.outputs),
                "allowed_models": ALLOWED_MODELS,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _plan(args: argparse.Namespace) -> int:
    _, plan = prepare_workspace(
        args.workspace,
        _task_path(args),
        profile=args.profile,
        single_model=args.model,
    )
    print(args.workspace / ".cofa" / "plan.json")
    print("Roles: " + ", ".join(role["name"] for role in plan["roles"]))
    return 0


def _run(args: argparse.Namespace) -> int:
    model = canonical_model(args.model or "gpt-6.1-sol")
    if args.mode == "multi-agent":
        result = run_multi_agent(
            args.workspace,
            _task_path(args),
            model=model,
            profile=args.profile,
            dry_run=args.dry_run,
            speed=args.speed,
        )
        print("Command: " + " ".join(result.command))
        return result.returncode
    results = run_sequential(
        args.workspace,
        _task_path(args),
        profile=args.profile,
        single_model=model if args.model is not None else None,
        dry_run=args.dry_run,
        speed=args.speed,
    )
    for result in results:
        print("Command: " + " ".join(result.command))
    return results[-1].returncode if results else 1


def _status(args: argparse.Namespace) -> int:
    plan = args.workspace / ".cofa" / "plan.json"
    data = {
        "workspace": str(args.workspace),
        "post_submission_locked": lock_path(args.workspace).exists(),
        "plan_ready": plan.exists(),
        "external_ai_credentials_present": sorted(
            key
            for key in (
                "OPENAI_API_KEY",
                "OPENROUTER_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
            )
            if os.environ.get(key)
        ),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            return _init(args)
        if args.command == "validate":
            return _validate(args)
        if args.command == "plan":
            return _plan(args)
        if args.command == "run":
            return _run(args)
        if args.command == "lock":
            marker = create_post_submission_lock(args.workspace)
            print(f"Post-submission AI lock created: {marker}")
            return 0
        if args.command == "status":
            return _status(args)
    except (PolicyViolation, SpecError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

