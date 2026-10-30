"""Deterministic role selection, model routing, and handoff planning."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .policy import canonical_model
from .spec import TaskSpec


ROLE_ORDER = ("planner", "implementer", "tester", "reviewer", "packager")

ROLE_DEPENDENCIES = {
    "planner": [],
    "implementer": ["planner"],
    "tester": ["implementer"],
    "reviewer": ["planner", "implementer", "tester"],
    "packager": ["tester", "reviewer"],
}

MODEL_PROFILES = {
    "balanced": {
        "planner": "gpt-6.1-sol",
        "implementer": "gpt-5.6-terra",
        "tester": "gpt-6-sol",
        "reviewer": "gpt-6.1-sol",
        "packager": "gpt-6-luna",
    },
    "quality": {role: "gpt-6.1-sol" for role in ROLE_ORDER},
    "fast": {
        "planner": "gpt-6-sol",
        "implementer": "gpt-5.6-terra",
        "tester": "gpt-6-luna",
        "reviewer": "gpt-6-sol",
        "packager": "gpt-6-luna",
    },
}


def _task_id(spec: TaskSpec) -> str:
    canonical = json.dumps(
        spec.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def build_plan(
    spec: TaskSpec,
    profile: str = "balanced",
    single_model: str | None = None,
) -> dict[str, Any]:
    if profile not in MODEL_PROFILES:
        raise ValueError(f"Unknown profile {profile!r}. Choose: {', '.join(MODEL_PROFILES)}")
    models = dict(MODEL_PROFILES[profile])
    if single_model:
        selected = canonical_model(single_model)
        models = {role: selected for role in ROLE_ORDER}

    requirement_ids = [f"REQ-{index:03d}" for index in range(1, len(spec.requirements) + 1)]
    output_ids = [f"OUT-{index:03d}" for index in range(1, len(spec.outputs) + 1)]
    traceability = [
        {"id": req_id, "text": text, "owner": "implementer", "status": "pending"}
        for req_id, text in zip(requirement_ids, spec.requirements)
    ]
    outputs = [
        {"id": out_id, "text": text, "owner": "packager", "status": "pending"}
        for out_id, text in zip(output_ids, spec.outputs)
    ]

    role_tasks = {
        "planner": [
            "Decompose every requirement and output into an executable plan.",
            "Create a risk list and requirement-to-test traceability matrix.",
            "Identify independent work that can run concurrently without file conflicts.",
        ],
        "implementer": [
            *(f"Implement {req_id}: {text}" for req_id, text in zip(requirement_ids, spec.requirements)),
            "Record changed files and implementation evidence in the handoff.",
        ],
        "tester": [
            *(f"Verify {req_id}: {text}" for req_id, text in zip(requirement_ids, spec.requirements)),
            "Run relevant tests and report commands, results, and reproducible defects.",
        ],
        "reviewer": [
            "Independently audit every requirement, constraint, acceptance criterion, and output.",
            "Check for regressions, unsupported claims, policy violations, and missing evidence.",
        ],
        "packager": [
            *(f"Confirm local output {out_id}: {text}" for out_id, text in zip(output_ids, spec.outputs)),
            "Create a local submission manifest without uploading, pushing, or transmitting files.",
        ],
    }

    roles = [
        {
            "name": role,
            "suggested_model": canonical_model(models[role]),
            "depends_on": ROLE_DEPENDENCIES[role],
            "tasks": role_tasks[role],
            "handoff": f".cofa/handoffs/{role}.md",
        }
        for role in ROLE_ORDER
    ]
    return {
        "schema_version": 1,
        "task_id": _task_id(spec),
        "topic": spec.topic,
        "profile": profile,
        "roles": roles,
        "traceability": traceability,
        "outputs": outputs,
        "workflow": [
            "planner",
            "implementer",
            "tester",
            "reviewer",
            "implementer_if_defects",
            "tester_recheck_if_changed",
            "packager",
        ],
    }

