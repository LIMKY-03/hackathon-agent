"""Task specification parsing and validation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class SpecError(ValueError):
    """Raised for malformed or incomplete task specifications."""


def _clean_list(name: str, value: Any, *, required: bool = False) -> list[str]:
    if value is None:
        value = []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise SpecError(f"{name} must be a JSON array of strings.")
    cleaned = [item.strip() for item in value if item.strip()]
    if required and not cleaned:
        raise SpecError(f"{name} must contain at least one item.")
    return cleaned


@dataclass(frozen=True)
class TaskSpec:
    topic: str
    requirements: list[str]
    outputs: list[str]
    context: str = ""
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    time_budget_minutes: int = 180
    schema_version: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskSpec":
        if not isinstance(data, dict):
            raise SpecError("The task specification must be a JSON object.")
        topic = data.get("topic", "")
        if not isinstance(topic, str) or not topic.strip():
            raise SpecError("topic must be a non-empty string.")
        context = data.get("context", "")
        if not isinstance(context, str):
            raise SpecError("context must be a string.")
        budget = data.get("time_budget_minutes", 180)
        if not isinstance(budget, int) or isinstance(budget, bool) or not 1 <= budget <= 180:
            raise SpecError("time_budget_minutes must be an integer from 1 to 180.")
        version = data.get("schema_version", 1)
        if version != 1:
            raise SpecError(f"Unsupported schema_version: {version!r}.")
        return cls(
            topic=topic.strip(),
            context=context.strip(),
            requirements=_clean_list("requirements", data.get("requirements"), required=True),
            constraints=_clean_list("constraints", data.get("constraints")),
            outputs=_clean_list("outputs", data.get("outputs"), required=True),
            acceptance_criteria=_clean_list(
                "acceptance_criteria", data.get("acceptance_criteria")
            ),
            time_budget_minutes=budget,
            schema_version=1,
        )

    @classmethod
    def load(cls, path: Path) -> "TaskSpec":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SpecError(f"Task file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise SpecError(f"Invalid JSON in {path}: {exc}") from exc
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {"schema_version": data.pop("schema_version"), **data}

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

