"""Non-bypassable contest policy checks used by every execution mode."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping


ALLOWED_MODELS = (
    "gpt-6.1-sol",
    "gpt-5.6-terra",
    "gpt-6-luna",
    "gpt-6-sol",
)

_MODEL_ALIASES = {
    "sol-6.1": "gpt-6.1-sol",
    "sol6.1": "gpt-6.1-sol",
    "gpt-6.1-sol": "gpt-6.1-sol",
    "terra-5.6": "gpt-5.6-terra",
    "terra5.6": "gpt-5.6-terra",
    "gpt-5.6-terra": "gpt-5.6-terra",
    "luna-6": "gpt-6-luna",
    "luna6": "gpt-6-luna",
    "gpt-6-luna": "gpt-6-luna",
    "sol-6.0": "gpt-6-sol",
    "sol6.0": "gpt-6-sol",
    "gpt-6-sol": "gpt-6-sol",
}

EXTERNAL_AI_CREDENTIALS = (
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AWS_BEDROCK_API_KEY",
)

LOCK_FILE = Path(".cofa") / "POST_SUBMISSION_LOCK"


class PolicyViolation(RuntimeError):
    """Raised when an operation conflicts with contest safety rules."""


def canonical_model(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-")
    try:
        return _MODEL_ALIASES[normalized]
    except KeyError as exc:
        allowed = ", ".join(ALLOWED_MODELS)
        raise PolicyViolation(
            f"Model {value!r} is not permitted. Allowed models: {allowed}."
        ) from exc


def assert_no_external_ai_credentials(
    environment: Mapping[str, str] | None = None,
) -> None:
    env = os.environ if environment is None else environment
    present = sorted(key for key in EXTERNAL_AI_CREDENTIALS if env.get(key))
    if present:
        raise PolicyViolation(
            "External/personal AI credential variables are set: "
            + ", ".join(present)
            + ". Remove them and use only the contest-provided Codex login."
        )


def lock_path(workspace: Path) -> Path:
    return workspace.resolve() / LOCK_FILE


def assert_not_post_submission(workspace: Path) -> None:
    marker = lock_path(workspace)
    if marker.exists():
        raise PolicyViolation(
            "Post-submission lock is active. AI execution is disabled for written "
            "follow-up questions."
        )


def create_post_submission_lock(workspace: Path) -> Path:
    marker = lock_path(workspace)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        "Submission finalized. Do not use AI for post-submission questions.\n",
        encoding="utf-8",
    )
    return marker


def codex_safety_feature_args() -> list[str]:
    """Disable prohibited interactive automation surfaces for every run."""
    return [
        "--disable",
        "computer_use",
        "--disable",
        "browser_use",
        "--disable",
        "browser_use_external",
        "--disable",
        "in_app_browser",
    ]

