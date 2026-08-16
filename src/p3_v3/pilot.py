"""Pilot-only foundation isolation. Not a confirmatory denominator."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)

PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"
PILOT_SCHEMA_PREFIX = "p3-pilot-"

CANONICAL_FOUNDATION_VERDICT_PATH = Path(
    "docs/review_20260816/boost_math_pilot_foundation_sol_high_review.md"
)
FOUNDATION_MARKDOWN_PATH = Path(
    "docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md"
)
FOUNDATION_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
PILOT_PLAN_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "plan_class": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "markdown_plan_sha256": str,
    "sol_high_plan_verdict_sha256": str,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "artifact_sha256": str,
}

_PLAN_LITERALS = {
    "schema_version": "p3-pilot-plan-v1",
    "execution_class": PILOT_EXECUTION_CLASS,
    "denominator": PILOT_DENOMINATOR,
    "plan_class": "PILOT_FOUNDATION_ONLY",
    "p12_item_id": "C-BOOSTMATH-001",
    "neutral_snapshot_id": (
        "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
    ),
    "normalized_source_tree_sha256": (
        "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
    ),
    "controlled_subject_id": (
        "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914"
    ),
    "controlled_subject_source_id": (
        "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
    ),
    "claims": "blocked",
    "formal_denominator_membership": False,
    "rq4_supported": False,
}


def is_pilot_artifact(value: Mapping[str, Any]) -> bool:
    schema = value.get("schema_version")
    execution = value.get("execution_class")
    denominator = value.get("denominator")
    return (
        (isinstance(schema, str) and schema.startswith(PILOT_SCHEMA_PREFIX))
        or execution == PILOT_EXECUTION_CLASS
        or denominator == PILOT_DENOMINATOR
    )


def reject_confirmatory_pilot(value: Mapping[str, Any], context: str) -> None:
    if is_pilot_artifact(value):
        raise EvidenceError(
            "E_PILOT_DENOMINATOR_LEAK",
            f"{context} rejected PILOT_ONLY or p3-pilot schema",
        )


def validate_foundation_verdict(
    value: object, markdown_plan_sha256: str
) -> dict[str, Any]:
    try:
        validated = validate_exact_object(
            value, FOUNDATION_VERDICT_EXACT, "foundation-verdict"
        )
        validate_sha256(
            validated["reviewed_plan_sha256"],
            "foundation-verdict.reviewed_plan_sha256",
        )
    except EvidenceError as exc:
        if exc.code in {"E_SCHEMA_KEYS", "E_SCHEMA_TYPE", "E_SHA256"}:
            raise EvidenceError("E_PILOT_PLAN_VERDICT", str(exc)) from exc
        raise
    if validated["reviewed_plan_path"] != FOUNDATION_MARKDOWN_PATH.as_posix():
        raise EvidenceError("E_PILOT_PLAN_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != markdown_plan_sha256:
        raise EvidenceError("E_PILOT_PLAN_VERDICT", "reviewed plan hash differs")
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_PLAN_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_PLAN_FROZEN":
        raise EvidenceError(
            "E_PILOT_PLAN_VERDICT", "authorized_state is not PILOT_PLAN_FROZEN"
        )
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_PLAN_VERDICT", "claims are not blocked")
    return validated


def validate_pilot_plan(value: object) -> dict[str, Any]:
    validated = validate_exact_object(value, PILOT_PLAN_EXACT, "p3-pilot-plan-v1")
    validate_sha256(
        validated["markdown_plan_sha256"], "p3-pilot-plan-v1.markdown_plan_sha256"
    )
    validate_sha256(
        validated["sol_high_plan_verdict_sha256"],
        "p3-pilot-plan-v1.sol_high_plan_verdict_sha256",
    )
    validate_sha256(validated["artifact_sha256"], "p3-pilot-plan-v1.artifact_sha256")
    if validated["predecessor_sha256"] != sorted(
        [
            validated["markdown_plan_sha256"],
            validated["sol_high_plan_verdict_sha256"],
        ]
    ):
        raise EvidenceError(
            "E_PILOT_PLAN_PREDECESSOR",
            "predecessor_sha256 must equal the sorted markdown and verdict hashes",
        )
    for key, expected in _PLAN_LITERALS.items():
        if validated[key] != expected:
            raise EvidenceError(
                "E_PILOT_PLAN_LITERAL",
                f"p3-pilot-plan-v1.{key} differs",
            )
    body = {key: item for key, item in validated.items() if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_PLAN_HASH", "pilot plan self-hash differs")
    return validated


def _read_foundation_verdict(markdown_plan_sha256: str) -> str:
    path = Path(CANONICAL_FOUNDATION_VERDICT_PATH)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise EvidenceError(
            "E_PILOT_PLAN_VERDICT",
            "canonical foundation verdict is not a regular file",
        )
    if not path.exists():
        raise EvidenceError(
            "E_PILOT_PLAN_VERDICT_ABSENT",
            "canonical foundation verdict is absent",
        )
    raw = path.read_bytes()
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
        is_canonical = (
            isinstance(parsed, dict) and canonical_json_bytes(parsed) == raw
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError(
            "E_PILOT_PLAN_VERDICT",
            "canonical foundation verdict is not canonical JSON",
        ) from exc
    if not is_canonical:
        raise EvidenceError(
            "E_PILOT_PLAN_VERDICT",
            "canonical foundation verdict is not canonical JSON",
        )
    validate_foundation_verdict(parsed, markdown_plan_sha256)
    return hashlib.sha256(raw).hexdigest()


def write_pilot_plan(markdown_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    markdown = Path(markdown_path)
    markdown_plan_sha256 = file_sha256(markdown)
    verdict_sha256 = _read_foundation_verdict(markdown_plan_sha256)
    body = {
        "schema_version": "p3-pilot-plan-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "plan_class": "PILOT_FOUNDATION_ONLY",
        "p12_item_id": "C-BOOSTMATH-001",
        "neutral_snapshot_id": _PLAN_LITERALS["neutral_snapshot_id"],
        "normalized_source_tree_sha256": _PLAN_LITERALS[
            "normalized_source_tree_sha256"
        ],
        "controlled_subject_id": _PLAN_LITERALS["controlled_subject_id"],
        "controlled_subject_source_id": _PLAN_LITERALS[
            "controlled_subject_source_id"
        ],
        "predecessor_sha256": sorted([markdown_plan_sha256, verdict_sha256]),
        "markdown_plan_sha256": markdown_plan_sha256,
        "sol_high_plan_verdict_sha256": verdict_sha256,
        "claims": "blocked",
        "formal_denominator_membership": False,
        "rq4_supported": False,
    }
    value = {**body, "artifact_sha256": canonical_sha256(body)}
    write_canonical_json(output_path, value, exclusive=True)
    return validate_pilot_plan(read_canonical_json(output_path))
