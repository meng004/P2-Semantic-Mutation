"""Immutable scientific-attempt records and phase-close receipts."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

from .artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_canonical_json,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from .bridge_and_frames import INFRASTRUCTURE_RETRY_LIMIT, P12_OUTCOME_STATES

TERMINAL_STATES = {
    "PASS",
    "FAIL_SCIENTIFIC",
    "FAIL_INFRASTRUCTURE",
    "INCONCLUSIVE",
    "MISSING_WITH_REASON",
}
JOB_ROLES = {
    "PRIMARY_CONTROLLED",
    "P12",
    "CONTRACT_SENSITIVITY",
    "PROFILING",
}
_ROLE_REQUIRED_INPUT_CLASS = {
    "PRIMARY_CONTROLLED": "E_COMMON",
    "P12": "E_COMMON",
    "CONTRACT_SENSITIVITY": "E_CONTRACT",
    "PROFILING": "E_COMMON",
}
FORBIDDEN_EVALUATION_INPUT_CLASSES = frozenset({"PROFILING", "CERTIFICATION_WITNESS"})
_LOWER_OUTCOMES = frozenset({"MR_VIOLATION", "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION"})
_COMPLETE_CASE_OUTCOMES = frozenset(
    {
        "MR_VIOLATION",
        "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
        "MR_SATISFIED",
    }
)
_UPPER_EXTRA_OUTCOMES = frozenset(
    {"SCIENTIFIC_INCONCLUSIVE", "INFRASTRUCTURE_UNRESOLVED"}
)
_INTENT_SCHEMA = {
    "job_id": str,
    "protocol_sha256": str,
    "phase": str,
    "argv": list,
    "cwd_identity": str,
    "environment_sha256": str,
    "input_sha256": list,
    "seed": (int, type(None)),
    "timeout_seconds": int,
    "attempt": int,
    "object_type": str,
    "object_id": str,
    "mr_id": str,
    "evaluation_input_class": str,
    "evaluation_input_id": str,
    "repetition_id": int,
    "environment_id": str,
    "job_role": str,
}
_RESULT_SCHEMA = {
    "job_id": str,
    "attempt": int,
    "status": str,
    "exit_code": (int, type(None)),
    "stdout_sha256": str,
    "stderr_sha256": str,
    "duration_seconds": (int, float),
    "failure_code": str,
    "scientific_outcome": (str, type(None)),
    "call_trace_sha256": (str, type(None)),
    "call_trace_identity": (str, type(None)),
}
_EVENT_SCHEMA = {
    "sequence": int,
    "kind": str,
    "phase": str,
    "job_id": str,
    "attempt": int,
    "artifact_sha256": str,
    "status": (str, type(None)),
    "previous_event_sha256": (str, type(None)),
    "event_sha256": str,
}
_P12_JOB_SCHEMA = {
    "job_id": str,
    "object_type": str,
    "object_id": str,
    "mr_id": str,
    "evaluation_input_class": str,
    "evaluation_input_id": str,
    "repetition_id": int,
    "environment_id": str,
    "job_role": str,
    "weight": int,
}
_P12_RESULT_SCHEMA = {
    "job_id": str,
    "scientific_outcome": str,
}
_DENOMINATOR_SCHEMA = {
    "schema_version": str,
    "p12_paired_ids": list,
    "jobs": list,
    "planned_count": int,
    "job_inventory_sha256": str,
    "paired_ids_sha256": str,
    "artifact_sha256": str,
}
_TERMINAL_P12_SCHEMA = {"intent": dict, "result": dict}
_LOCKED_JOB_SCHEMA = {
    "job_id": str,
    "phase": str,
    "job_role": str,
    "object_identity": str,
    "input_identity_sha256": str,
    "intent_template_sha256": str,
    "maximum_attempts": int,
    "retry_trigger": str,
    "execution_class": str,
    "p12_access_class": str,
}
_EXECUTION_CLASSES = frozenset(
    {"SYNTHETIC_INFRASTRUCTURE", "NON_SCIENTIFIC_CONTROL", "REAL_SCIENTIFIC"}
)
_P12_ACCESS_CLASSES = frozenset({"FORBIDDEN", "PERMITTED", "REQUIRED"})
_CLAIM_SCHEMA = {
    "claim_id": str,
    "rqs": list,
    "evidence_references": list,
    "status": str,
    "artifact_sha256": str,
}
_CLAIM_LEDGER_SCHEMA = {
    "schema_version": str,
    "claim_authority_sha256": str,
    "rq_authority_sha256": str,
    "claims": list,
    "artifact_sha256": str,
}
_PHASE_IDS = tuple(f"PHASE_{number}" for number in range(8))
_PHASE_RECEIPT_SCHEMA = {
    "phase_id": str,
    "phase_status": str,
    "protocol_sha256": str,
    "expected_job_inventory_sha256": str,
    "expected_job_count": int,
    "terminal_result_count": int,
    "ledger_event_count": int,
    "ledger_head_sha256": (str, type(None)),
    "ledger_raw_sha256": str,
    "output_manifest_sha256": str,
    "artifact_sha256": str,
}


def _validate_intent(intent: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(intent), _INTENT_SCHEMA, "intent")
    if not value["job_id"] or "/" in value["job_id"]:
        raise EvidenceError("E_JOB_ID", "job ID must be a nonempty path segment")
    validate_sha256(value["protocol_sha256"], "intent.protocol_sha256")
    validate_sha256(value["environment_sha256"], "intent.environment_sha256")
    if not value["argv"] or any(
        type(item) is not str or not item for item in value["argv"]
    ):
        raise EvidenceError(
            "E_INTENT_ARGV", "intent argv must contain nonempty strings"
        )
    if value["input_sha256"] != sorted(set(value["input_sha256"])):
        raise EvidenceError("E_INTENT_INPUTS", "input hashes must be sorted and unique")
    for index, digest in enumerate(value["input_sha256"]):
        validate_sha256(digest, f"intent.input_sha256[{index}]")
    if type(value["seed"]) is bool:
        raise EvidenceError("E_INTENT_SEED", "seed cannot be boolean")
    if value["attempt"] < 1 or value["timeout_seconds"] < 1:
        raise EvidenceError("E_INTENT_RANGE", "attempt and timeout must be positive")
    if type(value["repetition_id"]) is bool or value["repetition_id"] < 1:
        raise EvidenceError("E_INTENT_REPETITION", "repetition_id must be positive")
    for field in (
        "object_type",
        "object_id",
        "mr_id",
        "evaluation_input_id",
        "environment_id",
    ):
        if not value[field]:
            raise EvidenceError("E_INTENT_IDENTITY", f"{field} must be nonempty")
    if value["job_role"] not in JOB_ROLES:
        raise EvidenceError(
            "E_JOB_ROLE", f"unsupported job role: {value['job_role']!r}"
        )
    if value["evaluation_input_class"] in FORBIDDEN_EVALUATION_INPUT_CLASSES:
        raise EvidenceError(
            "E_EVALUATION_INPUT_CLASS",
            f"evaluation input class is forbidden: {value['evaluation_input_class']}",
        )
    required_class = _ROLE_REQUIRED_INPUT_CLASS[value["job_role"]]
    if value["evaluation_input_class"] != required_class:
        raise EvidenceError(
            "E_JOB_ROLE_INPUT",
            f"{value['job_role']} requires evaluation_input_class={required_class}",
        )
    return value


def retry_invariant(intent: Mapping[str, Any]) -> dict[str, Any]:
    """Return the validated retry identity, excluding only its attempt number."""

    value = _validate_intent(intent)
    return {key: item for key, item in value.items() if key != "attempt"}


def intent_template_sha256(intent: Mapping[str, Any]) -> str:
    """Hash every validated production-intent field except the attempt number."""

    return canonical_sha256(retry_invariant(intent))


def _validate_result(
    result: Mapping[str, Any],
    intent: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value = validate_exact_object(dict(result), _RESULT_SCHEMA, "result")
    if value["status"] not in TERMINAL_STATES:
        raise EvidenceError("E_RESULT_STATUS", "result status is not terminal")
    for field in ("stdout_sha256", "stderr_sha256"):
        validate_sha256(value[field], f"result.{field}")
    if value["attempt"] < 1 or type(value["attempt"]) is bool:
        raise EvidenceError("E_RESULT_ATTEMPT", "result attempt must be positive")
    if value["duration_seconds"] < 0 or type(value["duration_seconds"]) is bool:
        raise EvidenceError("E_RESULT_DURATION", "duration cannot be negative")
    if value["status"] == "PASS" and (value["exit_code"] != 0 or value["failure_code"]):
        raise EvidenceError(
            "E_RESULT_PASS", "PASS must have exit 0 and no failure code"
        )
    if value["status"] != "PASS" and not value["failure_code"]:
        raise EvidenceError(
            "E_RESULT_FAILURE_CODE", "non-PASS result needs a failure code"
        )
    outcome = value["scientific_outcome"]
    phase7_p12 = (
        intent is not None
        and intent.get("phase") == "PHASE_7"
        and intent.get("job_role") == "P12"
    )
    if phase7_p12:
        if outcome not in P12_OUTCOME_STATES:
            raise EvidenceError(
                "E_SCIENTIFIC_OUTCOME",
                "Phase 7 P12 results require one of the five scientific outcomes",
            )
    elif outcome is not None:
        raise EvidenceError(
            "E_SCIENTIFIC_OUTCOME",
            "only Phase 7 P12 results may carry a scientific outcome",
        )
    trace_sha256 = value["call_trace_sha256"]
    trace_identity = value["call_trace_identity"]
    profiling = (
        intent is not None
        and intent.get("phase") == "PHASE_1"
        and intent.get("job_role") == "PROFILING"
        and intent.get("object_type") == "PROFILING_BEHAVIOR"
    )
    if profiling:
        if trace_sha256 is None or trace_identity is None:
            raise EvidenceError(
                "E_PROFILE_TRACE_BINDING",
                "profiling result requires a trace digest and identity",
            )
        validate_sha256(trace_sha256, "result.call_trace_sha256")
        validate_sha256(trace_identity, "result.call_trace_identity")
        expected_trace_identity = canonical_sha256(
            {
                "job_id": intent["job_id"],
                "attempt": intent["attempt"],
                "behavior_id": intent["object_id"],
                "call_trace_sha256": trace_sha256,
                "domain": "P3-PROFILING-TRACE-v1",
            }
        )
        if trace_identity != expected_trace_identity:
            raise EvidenceError(
                "E_PROFILE_TRACE_BINDING", "profiling trace identity differs"
            )
    elif trace_sha256 is not None or trace_identity is not None:
        raise EvidenceError(
            "E_PROFILE_TRACE_BINDING",
            "only a Phase 1 profiling attempt may bind a call trace",
        )
    return value


def create_intent(attempt_dir: str | Path, intent: Mapping[str, Any]) -> None:
    value = _validate_intent(intent)
    directory = Path(attempt_dir)
    if (
        directory.name != str(value["attempt"])
        or directory.parent.name != value["job_id"]
    ):
        raise EvidenceError(
            "E_INTENT_PATH", "attempt path does not match intent identity"
        )
    write_canonical_json(directory / "intent.json", value, exclusive=True)


def write_result(attempt_dir: str | Path, result: Mapping[str, Any]) -> None:
    directory = Path(attempt_dir)
    intent_path = directory / "intent.json"
    if not intent_path.exists():
        raise EvidenceError("E_RESULT_WITHOUT_INTENT", "result has no durable intent")
    intent = _validate_intent(read_canonical_json(intent_path))
    value = _validate_result(result, intent)
    if value["job_id"] != intent["job_id"] or value["attempt"] != intent["attempt"]:
        raise EvidenceError("E_RESULT_IDENTITY", "result identity differs from intent")
    write_canonical_json(directory / "result.json", value, exclusive=True)


def _event(
    sequence: int,
    kind: str,
    payload: Mapping[str, Any],
    previous: str | None,
    *,
    phase: str,
) -> dict:
    body = {
        "sequence": sequence,
        "kind": kind,
        "phase": phase,
        "job_id": payload["job_id"],
        "attempt": payload["attempt"],
        "artifact_sha256": canonical_sha256(payload),
        "status": payload.get("status"),
        "previous_event_sha256": previous,
    }
    return {**body, "event_sha256": canonical_sha256(body)}


def _write_exclusive_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise EvidenceError("E_EXISTS", f"artifact already exists: {path}") from exc
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def reduce_attempts(
    job_root: str | Path, ledger_path: str | Path
) -> list[dict[str, Any]]:
    root = Path(job_root)
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for job_directory in sorted(
        (item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name
    ):
        attempts: list[tuple[int, Path]] = []
        for attempt_directory in job_directory.iterdir():
            if not attempt_directory.is_dir() or not attempt_directory.name.isdecimal():
                raise EvidenceError(
                    "E_ATTEMPT_PATH", f"invalid attempt path: {attempt_directory}"
                )
            attempt_number = int(attempt_directory.name)
            if attempt_number < 1 or str(attempt_number) != attempt_directory.name:
                raise EvidenceError(
                    "E_ATTEMPT_PATH", f"noncanonical attempt: {attempt_directory}"
                )
            attempts.append((attempt_number, attempt_directory))
        attempts.sort()
        if [number for number, _ in attempts] != list(range(1, len(attempts) + 1)):
            raise EvidenceError(
                "E_ATTEMPT_SEQUENCE", "attempts must be contiguous from one"
            )
        if len(attempts) > INFRASTRUCTURE_RETRY_LIMIT:
            raise EvidenceError(
                "E_RETRY_POLICY",
                f"a job may have at most {INFRASTRUCTURE_RETRY_LIMIT} attempts",
            )
        previous_status: str | None = None
        expected_retry_invariant: bytes | None = None
        for attempt_number, attempt_directory in attempts:
            if attempt_number > 1 and previous_status != "FAIL_INFRASTRUCTURE":
                raise EvidenceError(
                    "E_RETRY_POLICY",
                    "only a completed infrastructure failure permits another attempt",
                )
            intent_path = attempt_directory / "intent.json"
            if not intent_path.exists():
                raise EvidenceError(
                    "E_ATTEMPT_INTENT", f"missing intent: {attempt_directory}"
                )
            intent = _validate_intent(read_canonical_json(intent_path))
            current_retry_invariant = canonical_json_bytes(retry_invariant(intent))
            if expected_retry_invariant is None:
                expected_retry_invariant = current_retry_invariant
            elif current_retry_invariant != expected_retry_invariant:
                raise EvidenceError(
                    "E_RETRY_IDENTITY",
                    "retry intent differs from the first attempt outside attempt",
                )
            if (
                intent["job_id"] != job_directory.name
                or intent["attempt"] != attempt_number
            ):
                raise EvidenceError(
                    "E_ATTEMPT_IDENTITY", "attempt directory identity differs"
                )
            intent_event = _event(
                len(events) + 1, "INTENT", intent, previous, phase=intent["phase"]
            )
            events.append(intent_event)
            previous = intent_event["event_sha256"]
            result_path = attempt_directory / "result.json"
            if result_path.exists():
                result = _validate_result(read_canonical_json(result_path), intent)
                if (
                    result["job_id"] != intent["job_id"]
                    or result["attempt"] != intent["attempt"]
                ):
                    raise EvidenceError(
                        "E_RESULT_IDENTITY", "result identity differs from intent"
                    )
                result_event = _event(
                    len(events) + 1,
                    "RESULT",
                    result,
                    previous,
                    phase=intent["phase"],
                )
                events.append(result_event)
                previous = result_event["event_sha256"]
                previous_status = result["status"]
            else:
                previous_status = None
    raw = b"".join(canonical_json_bytes(event) for event in events)
    _write_exclusive_bytes(Path(ledger_path), raw)
    return events


def _require_directory(path: Path, context: str) -> list[Path]:
    try:
        path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_ATTEMPT_TREE", f"missing {context}: {path}") from exc
    if path.is_symlink() or not path.is_dir():
        raise EvidenceError("E_ATTEMPT_TREE", f"{context} is not a directory: {path}")
    return list(path.iterdir())


def reconstruct_attempt_events(job_root: Path) -> list[dict[str, Any]]:
    """Rebuild canonical ledger events from the frozen phase/job/attempt tree."""

    root = Path(job_root)
    phase_entries = _require_directory(root, "job root")
    phase_directories: list[tuple[int, Path]] = []
    for phase_directory in phase_entries:
        if phase_directory.name not in _PHASE_IDS:
            raise EvidenceError(
                "E_ATTEMPT_TREE", f"unknown phase entry: {phase_directory.name}"
            )
        _require_directory(phase_directory, "phase entry")
        phase_directories.append(
            (_PHASE_IDS.index(phase_directory.name), phase_directory)
        )

    events: list[dict[str, Any]] = []
    previous: str | None = None
    for _, phase_directory in sorted(phase_directories):
        job_directories = _require_directory(phase_directory, "phase entry")
        if not job_directories:
            raise EvidenceError(
                "E_ATTEMPT_TREE", f"empty phase: {phase_directory.name}"
            )
        for job_directory in sorted(job_directories, key=lambda path: path.name):
            if not job_directory.name or "/" in job_directory.name:
                raise EvidenceError("E_ATTEMPT_TREE", "job ID is not a path segment")
            attempt_entries = _require_directory(job_directory, "job entry")
            attempts: list[tuple[int, Path]] = []
            for attempt_directory in attempt_entries:
                _require_directory(attempt_directory, "attempt entry")
                if not attempt_directory.name.isdecimal():
                    raise EvidenceError(
                        "E_ATTEMPT_TREE", f"invalid attempt path: {attempt_directory}"
                    )
                number = int(attempt_directory.name)
                if number < 1 or str(number) != attempt_directory.name:
                    raise EvidenceError(
                        "E_ATTEMPT_TREE", f"noncanonical attempt: {attempt_directory}"
                    )
                attempts.append((number, attempt_directory))
            attempts.sort()
            if not attempts or [number for number, _ in attempts] != list(
                range(1, len(attempts) + 1)
            ):
                raise EvidenceError(
                    "E_ATTEMPT_SEQUENCE", "attempts must be contiguous from one"
                )
            if len(attempts) > INFRASTRUCTURE_RETRY_LIMIT:
                raise EvidenceError(
                    "E_RETRY_POLICY",
                    f"a job may have at most {INFRASTRUCTURE_RETRY_LIMIT} attempts",
                )
            previous_status: str | None = None
            expected_retry_invariant: bytes | None = None
            for attempt_number, attempt_directory in attempts:
                if attempt_number > 1 and previous_status != "FAIL_INFRASTRUCTURE":
                    raise EvidenceError(
                        "E_RETRY_POLICY",
                        "only a completed infrastructure failure permits another attempt",
                    )
                entries = _require_directory(attempt_directory, "attempt entry")
                names = {entry.name for entry in entries}
                if names not in ({"intent.json"}, {"intent.json", "result.json"}):
                    raise EvidenceError(
                        "E_ATTEMPT_TREE",
                        f"attempt files differ from frozen grammar: {attempt_directory}",
                    )
                if any(entry.is_symlink() or not entry.is_file() for entry in entries):
                    raise EvidenceError(
                        "E_ATTEMPT_TREE",
                        f"attempt contains a non-regular file: {attempt_directory}",
                    )
                intent = _validate_intent(
                    read_canonical_json(attempt_directory / "intent.json")
                )
                if (
                    intent["phase"] != phase_directory.name
                    or intent["job_id"] != job_directory.name
                    or intent["attempt"] != attempt_number
                ):
                    raise EvidenceError(
                        "E_ATTEMPT_IDENTITY", "attempt directory identity differs"
                    )
                invariant = canonical_json_bytes(retry_invariant(intent))
                if expected_retry_invariant is None:
                    expected_retry_invariant = invariant
                elif invariant != expected_retry_invariant:
                    raise EvidenceError(
                        "E_RETRY_IDENTITY",
                        "retry intent differs from the first attempt outside attempt",
                    )
                intent_event = _event(
                    len(events) + 1,
                    "INTENT",
                    intent,
                    previous,
                    phase=phase_directory.name,
                )
                events.append(intent_event)
                previous = intent_event["event_sha256"]
                result_path = attempt_directory / "result.json"
                if result_path.exists():
                    result = _validate_result(read_canonical_json(result_path), intent)
                    if (
                        result["job_id"] != intent["job_id"]
                        or result["attempt"] != intent["attempt"]
                    ):
                        raise EvidenceError(
                            "E_RESULT_IDENTITY", "result identity differs from intent"
                        )
                    result_event = _event(
                        len(events) + 1,
                        "RESULT",
                        result,
                        previous,
                        phase=phase_directory.name,
                    )
                    events.append(result_event)
                    previous = result_event["event_sha256"]
                    previous_status = result["status"]
                else:
                    previous_status = None
    return events


def reconstruct_attempt_records(job_root: Path) -> list[dict[str, Any]]:
    """Return the exact validated intent/result records behind ledger events."""

    root = Path(job_root)
    reconstruct_attempt_events(root)
    records: list[dict[str, Any]] = []
    for phase_directory in sorted(
        root.iterdir(), key=lambda path: _PHASE_IDS.index(path.name)
    ):
        for job_directory in sorted(phase_directory.iterdir(), key=lambda path: path.name):
            for attempt_directory in sorted(
                job_directory.iterdir(), key=lambda path: int(path.name)
            ):
                intent = _validate_intent(
                    read_canonical_json(attempt_directory / "intent.json")
                )
                result_path = attempt_directory / "result.json"
                result = (
                    _validate_result(read_canonical_json(result_path), intent)
                    if result_path.exists()
                    else None
                )
                records.append({"intent": intent, "result": result})
    return records


def verify_attempt_tree(
    job_root: str | Path, ledger: str | Path
) -> list[dict[str, Any]]:
    """Require the supplied ledger to be the exact reconstruction of the tree."""

    events = reconstruct_attempt_events(Path(job_root))
    expected = b"".join(canonical_json_bytes(event) for event in events)
    if Path(ledger).read_bytes() != expected:
        raise EvidenceError(
            "E_LEDGER_RECONSTRUCTION", "ledger bytes differ from reconstructed attempts"
        )
    verified = verify_ledger(ledger)
    if verified != events:
        raise EvidenceError(
            "E_LEDGER_RECONSTRUCTION",
            "ledger events differ from reconstructed attempts",
        )
    return events


def _validate_locked_jobs(
    locked_jobs: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(locked_jobs, (str, bytes)) or not isinstance(locked_jobs, Sequence):
        raise EvidenceError("E_AUTHORITY_JOB_SET", "locked jobs must be a sequence")
    jobs: list[dict[str, Any]] = []
    for index, candidate in enumerate(locked_jobs):
        try:
            job = validate_exact_object(
                dict(candidate), _LOCKED_JOB_SCHEMA, f"locked_jobs[{index}]"
            )
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_JOB_SET", "locked job schema differs"
            ) from exc
        if (
            job["execution_class"] not in _EXECUTION_CLASSES
            or job["p12_access_class"] not in _P12_ACCESS_CLASSES
        ):
            raise EvidenceError(
                "E_AUTHORITY_EXECUTION_CLASS",
                "locked execution or P12-access class is invalid",
            )
        try:
            for field in (
                "job_id",
                "input_identity_sha256",
                "intent_template_sha256",
            ):
                validate_sha256(job[field], f"locked_jobs[{index}].{field}")
        except EvidenceError as exc:
            raise EvidenceError(
                "E_AUTHORITY_JOB_SET", "locked job digest differs"
            ) from exc
        if (
            not job["phase"]
            or not job["job_role"]
            or not job["object_identity"]
            or job["maximum_attempts"] != INFRASTRUCTURE_RETRY_LIMIT
            or job["retry_trigger"] != "FAIL_INFRASTRUCTURE"
        ):
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "locked retry or intent metadata differs"
            )
        jobs.append(job)
    job_ids = [job["job_id"] for job in jobs]
    template_ids = [job["intent_template_sha256"] for job in jobs]
    if (
        not jobs
        or job_ids != sorted(job_ids)
        or len(job_ids) != len(set(job_ids))
        or len(template_ids) != len(set(template_ids))
    ):
        raise EvidenceError(
            "E_AUTHORITY_JOB_SET", "locked jobs are not sorted and unique"
        )
    return jobs


def verify_locked_execution(
    locked_jobs: Sequence[Mapping[str, Any]],
    job_root: Path,
    ledger_path: Path,
) -> dict[str, Any]:
    """Match complete attempt records to externally locked base-job authority."""

    jobs = _validate_locked_jobs(locked_jobs)
    try:
        records = reconstruct_attempt_records(Path(job_root))
    except EvidenceError as exc:
        raise EvidenceError(
            "E_AUTHORITY_INTENT", "attempt tree differs from locked intent authority"
        ) from exc
    by_job = {job["job_id"]: job for job in jobs}
    record_job_ids = sorted({record["intent"]["job_id"] for record in records})
    if record_job_ids != list(by_job):
        if len(record_job_ids) == len(by_job):
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "recorded job identity differs from the lock"
            )
        raise EvidenceError(
            "E_AUTHORITY_JOB_SET", "recorded base-job set differs from the lock"
        )

    latest: dict[str, dict[str, Any]] = {}
    for record in records:
        intent = record["intent"]
        locked = by_job[intent["job_id"]]
        expected = {
            "phase": intent["phase"],
            "job_role": intent["job_role"],
            "object_identity": f'{intent["object_type"]}:{intent["object_id"]}',
            "input_identity_sha256": canonical_sha256(intent["input_sha256"]),
            "intent_template_sha256": intent_template_sha256(intent),
        }
        if any(locked[field] != value for field, value in expected.items()):
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "recorded intent differs from locked authority"
            )
        if intent["attempt"] > locked["maximum_attempts"]:
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "recorded attempt exceeds locked retry policy"
            )
        latest[intent["job_id"]] = record

    try:
        verify_attempt_tree(job_root, ledger_path)
    except (OSError, EvidenceError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_INTENT", "ledger differs from complete attempt records"
        ) from exc
    return {
        "authorized_real_p12_job_count": sum(
            job["p12_access_class"] in {"PERMITTED", "REQUIRED"} for job in jobs
        ),
        "recorded_real_scientific_terminal_count": sum(
            job["execution_class"] == "REAL_SCIENTIFIC"
            and latest[job["job_id"]]["result"] is not None
            for job in jobs
        ),
    }


def verify_ledger(ledger_path: str | Path) -> list[dict[str, Any]]:
    raw = Path(ledger_path).read_bytes()
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        try:
            event = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceError(
                "E_LEDGER_JSON", f"invalid ledger line {line_number}"
            ) from exc
        if canonical_json_bytes(event) != line:
            raise EvidenceError(
                "E_LEDGER_CANONICAL", f"noncanonical ledger line {line_number}"
            )
        validate_exact_object(event, _EVENT_SCHEMA, f"ledger[{line_number}]")
        validate_sha256(
            event["artifact_sha256"], f"ledger[{line_number}].artifact_sha256"
        )
        validate_sha256(event["event_sha256"], f"ledger[{line_number}].event_sha256")
        if event["previous_event_sha256"] is not None:
            validate_sha256(
                event["previous_event_sha256"],
                f"ledger[{line_number}].previous_event_sha256",
            )
        if event["kind"] == "INTENT" and event["status"] is not None:
            raise EvidenceError("E_LEDGER_STATUS", "intent event cannot have status")
        if event["kind"] == "RESULT" and event["status"] not in TERMINAL_STATES:
            raise EvidenceError(
                "E_LEDGER_STATUS", "result event status is not terminal"
            )
        if event["kind"] not in {"INTENT", "RESULT"}:
            raise EvidenceError("E_LEDGER_KIND", f"unknown event kind: {event['kind']}")
        body = {key: value for key, value in event.items() if key != "event_sha256"}
        if event["event_sha256"] != canonical_sha256(body):
            raise EvidenceError(
                "E_LEDGER_EVENT_HASH", f"event hash differs at {line_number}"
            )
        if (
            event["sequence"] != line_number
            or event["previous_event_sha256"] != previous
        ):
            raise EvidenceError(
                "E_LEDGER_CHAIN", f"event chain differs at {line_number}"
            )
        previous = event["event_sha256"]
        events.append(event)
    return events


def close_phase(
    phase_id: str,
    protocol_sha256: str,
    expected_jobs: Sequence[str],
    ledger_path: str | Path,
    output_manifest_sha256: str,
) -> dict[str, Any]:
    if not isinstance(phase_id, str) or not phase_id or "/" in phase_id:
        raise EvidenceError("E_PHASE_ID", "phase ID must be a nonempty path segment")
    validate_sha256(protocol_sha256, "protocol_sha256")
    validate_sha256(output_manifest_sha256, "output_manifest_sha256")
    expected = list(expected_jobs)
    if expected != sorted(set(expected)) or any(
        not item or "/" in item for item in expected
    ):
        raise EvidenceError(
            "E_PHASE_JOBS", "expected jobs must be sorted unique path segments"
        )
    all_events = verify_ledger(ledger_path)
    events = [event for event in all_events if event["phase"] == phase_id]
    intents: dict[tuple[str, int], dict] = {}
    results: dict[tuple[str, int], dict] = {}
    for event in events:
        key = (event["job_id"], event["attempt"])
        if event["kind"] == "INTENT":
            intents[key] = event
        elif event["kind"] == "RESULT":
            results[key] = event
        else:
            raise EvidenceError("E_LEDGER_KIND", f"unknown event kind: {event['kind']}")
    if set(intents) != set(results):
        raise EvidenceError("E_PHASE_PENDING", "phase contains pending attempts")
    observed_jobs = sorted({job_id for job_id, _ in intents})
    if observed_jobs != expected:
        raise EvidenceError(
            "E_PHASE_JOB_SET", "ledger jobs differ from expected inventory"
        )
    ledger_raw = b"".join(canonical_json_bytes(event) for event in events)
    body = {
        "phase_id": phase_id,
        "phase_status": "CLOSED",
        "protocol_sha256": protocol_sha256,
        "expected_job_inventory_sha256": canonical_sha256(expected),
        "expected_job_count": len(expected),
        "terminal_result_count": len(results),
        "ledger_event_count": len(events),
        "ledger_head_sha256": events[-1]["event_sha256"] if events else None,
        "ledger_raw_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "output_manifest_sha256": output_manifest_sha256,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def verify_phase_receipt(
    receipt: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    expected_jobs: Sequence[str],
    output_manifest: Mapping[str, Any] | str,
) -> None:
    """Recompute a closed phase receipt from reconstructed events."""

    value = validate_exact_object(dict(receipt), _PHASE_RECEIPT_SCHEMA, "phase_receipt")
    if value["phase_id"] not in _PHASE_IDS:
        raise EvidenceError("E_PHASE_RECEIPT", "phase receipt has an unknown phase")
    if value["phase_status"] != "CLOSED":
        raise EvidenceError("E_PHASE_RECEIPT", "phase receipt is not closed")
    validate_sha256(value["protocol_sha256"], "phase_receipt.protocol_sha256")
    if isinstance(output_manifest, str):
        output_sha256 = validate_sha256(output_manifest, "output_manifest_sha256")
    elif isinstance(output_manifest, Mapping):
        output_value = dict(output_manifest)
        output_sha256 = validate_sha256(
            output_value.get("artifact_sha256"), "output_manifest.artifact_sha256"
        )
        output_body = {
            key: item for key, item in output_value.items() if key != "artifact_sha256"
        }
        if output_sha256 != canonical_sha256(output_body):
            raise EvidenceError("E_PHASE_RECEIPT", "output manifest self-hash differs")
    else:
        raise EvidenceError("E_PHASE_RECEIPT", "output manifest must be an object")
    expected = list(expected_jobs)
    if expected != sorted(set(expected)) or any(
        type(item) is not str or not item or "/" in item for item in expected
    ):
        raise EvidenceError("E_PHASE_RECEIPT", "expected jobs are not canonical")
    normalized_events = [dict(event) for event in events]
    for index, event in enumerate(normalized_events):
        validate_exact_object(event, _EVENT_SCHEMA, f"phase_events[{index}]")
        if event["phase"] != value["phase_id"]:
            raise EvidenceError(
                "E_PHASE_RECEIPT", "phase receipt contains an event from another phase"
            )
    ledger_raw = b"".join(canonical_json_bytes(event) for event in normalized_events)
    intents = {
        (event["job_id"], event["attempt"]): event
        for event in normalized_events
        if event.get("kind") == "INTENT"
    }
    results = {
        (event["job_id"], event["attempt"]): event
        for event in normalized_events
        if event.get("kind") == "RESULT"
    }
    observed_jobs = sorted({job_id for job_id, _ in intents})
    closed = set(intents) == set(results) and observed_jobs == expected
    body = {
        "phase_id": value["phase_id"],
        "phase_status": "CLOSED" if closed else "OPEN",
        "protocol_sha256": value["protocol_sha256"],
        "expected_job_inventory_sha256": canonical_sha256(expected),
        "expected_job_count": len(expected),
        "terminal_result_count": len(results),
        "ledger_event_count": len(normalized_events),
        "ledger_head_sha256": (
            normalized_events[-1]["event_sha256"] if normalized_events else None
        ),
        "ledger_raw_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "output_manifest_sha256": output_sha256,
    }
    rebuilt = {**body, "artifact_sha256": canonical_sha256(body)}
    if rebuilt != value:
        raise EvidenceError(
            "E_PHASE_RECEIPT", "phase receipt differs from reconstructed evidence"
        )


def _validate_p12_job(job: Mapping[str, Any], index: int) -> dict[str, Any]:
    value = validate_exact_object(dict(job), _P12_JOB_SCHEMA, f"job_records[{index}]")
    if not value["job_id"] or "/" in value["job_id"]:
        raise EvidenceError("E_JOB_ID", "job ID must be a nonempty path segment")
    if value["job_role"] != "P12":
        raise EvidenceError(
            "E_P12_JOB_ROLE", "P12 denominator jobs require job_role=P12"
        )
    if value["evaluation_input_class"] != "E_COMMON":
        raise EvidenceError(
            "E_P12_INPUT_CLASS",
            "P12 denominator jobs require evaluation_input_class=E_COMMON",
        )
    if type(value["weight"]) is bool or value["weight"] != 1:
        raise EvidenceError("E_P12_WEIGHT", "P12 denominator weights must equal one")
    if type(value["repetition_id"]) is bool or value["repetition_id"] < 1:
        raise EvidenceError("E_P12_REPETITION", "repetition_id must be positive")
    for field in (
        "object_type",
        "object_id",
        "mr_id",
        "evaluation_input_id",
        "environment_id",
    ):
        if not value[field]:
            raise EvidenceError("E_P12_IDENTITY", f"{field} must be nonempty")
    return value


def freeze_p12_denominator(
    paired_ids: Sequence[str],
    job_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    paired = list(paired_ids)
    if paired != sorted(set(paired)) or any(
        not item or not isinstance(item, str) for item in paired
    ):
        raise EvidenceError(
            "E_P12_PAIRED", "P12_PAIRED ids must be sorted unique nonempty strings"
        )
    jobs: list[dict[str, Any]] = []
    seen_job_ids: set[str] = set()
    referenced: set[str] = set()
    for index, candidate in enumerate(job_records):
        job = _validate_p12_job(candidate, index)
        if job["job_id"] in seen_job_ids:
            raise EvidenceError("E_P12_JOB_SET", f"duplicate job_id: {job['job_id']}")
        seen_job_ids.add(job["job_id"])
        if job["object_id"] not in paired:
            raise EvidenceError(
                "E_P12_PAIRED",
                f"job object_id not in P12_PAIRED: {job['object_id']}",
            )
        referenced.add(job["object_id"])
        jobs.append(job)
    jobs.sort(key=lambda item: item["job_id"])
    if referenced != set(paired):
        raise EvidenceError(
            "E_P12_PAIRED",
            "P12_PAIRED membership differs from denominator job object_ids",
        )
    body = {
        "schema_version": "p3-p12-denominator-v1",
        "p12_paired_ids": paired,
        "jobs": jobs,
        "planned_count": len(jobs),
        "job_inventory_sha256": canonical_sha256(jobs),
        "paired_ids_sha256": canonical_sha256(paired),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def verify_p12_denominator(denominator: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(denominator), _DENOMINATOR_SCHEMA, "denominator")
    if value["schema_version"] != "p3-p12-denominator-v1":
        raise EvidenceError("E_P12_DENOMINATOR", "unsupported P12 denominator schema")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_P12_DENOMINATOR", "denominator self-hash differs")
    rebuilt = freeze_p12_denominator(value["p12_paired_ids"], value["jobs"])
    if rebuilt != value:
        if rebuilt["p12_paired_ids"] != value["p12_paired_ids"]:
            raise EvidenceError("E_P12_PAIRED", "P12_PAIRED membership was altered")
        if any(
            left.get("weight") != right.get("weight")
            for left, right in zip(rebuilt["jobs"], value["jobs"])
        ):
            raise EvidenceError("E_P12_WEIGHT", "P12 denominator weights were altered")
        raise EvidenceError("E_P12_DENOMINATOR", "denominator contents were altered")
    return value


# Backward-compatible private alias used by summarize_p12_outcomes.
_verify_p12_denominator = verify_p12_denominator


def summarize_p12_outcomes(
    denominator: Mapping[str, Any],
    results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    frozen = _verify_p12_denominator(denominator)
    planned_ids = [job["job_id"] for job in frozen["jobs"]]
    planned_set = set(planned_ids)
    observed: dict[str, str] = {}
    for index, candidate in enumerate(results):
        row = validate_exact_object(
            dict(candidate), _P12_RESULT_SCHEMA, f"results[{index}]"
        )
        if row["job_id"] not in planned_set:
            raise EvidenceError(
                "E_P12_JOB_SET", f"unexpected result job_id: {row['job_id']}"
            )
        if row["job_id"] in observed:
            raise EvidenceError(
                "E_P12_JOB_SET", f"duplicate result job_id: {row['job_id']}"
            )
        if row["scientific_outcome"] not in P12_OUTCOME_STATES:
            raise EvidenceError(
                "E_SCIENTIFIC_OUTCOME",
                f"unknown scientific outcome: {row['scientific_outcome']}",
            )
        observed[row["job_id"]] = row["scientific_outcome"]
    if set(observed) != planned_set:
        raise EvidenceError(
            "E_P12_JOB_SET",
            "result job set differs from frozen P12 denominator",
        )
    state_counts = {state: 0 for state in P12_OUTCOME_STATES}
    for job_id in planned_ids:
        state_counts[observed[job_id]] += 1
    planned_count = frozen["planned_count"]
    lower_numerator = sum(state_counts[state] for state in _LOWER_OUTCOMES)
    upper_numerator = lower_numerator + sum(
        state_counts[state] for state in _UPPER_EXTRA_OUTCOMES
    )
    complete_case_denominator = sum(
        state_counts[state] for state in _COMPLETE_CASE_OUTCOMES
    )
    complete_case_numerator = lower_numerator
    if planned_count == 0:
        lower_rate = str(Fraction(0, 1))
        upper_rate = str(Fraction(0, 1))
    else:
        lower_rate = str(Fraction(lower_numerator, planned_count))
        upper_rate = str(Fraction(upper_numerator, planned_count))
    if complete_case_denominator == 0:
        complete_case_rate = str(Fraction(0, 1))
    else:
        complete_case_rate = str(
            Fraction(complete_case_numerator, complete_case_denominator)
        )
    body = {
        "planned_count": planned_count,
        "state_counts": state_counts,
        "lower_numerator": lower_numerator,
        "lower_rate": lower_rate,
        "upper_numerator": upper_numerator,
        "upper_rate": upper_rate,
        "complete_case_numerator": complete_case_numerator,
        "complete_case_denominator": complete_case_denominator,
        "complete_case_rate": complete_case_rate,
        "scientific_inconclusive_count": state_counts["SCIENTIFIC_INCONCLUSIVE"],
        "infrastructure_unresolved_count": state_counts["INFRASTRUCTURE_UNRESOLVED"],
        "denominator_sha256": frozen["artifact_sha256"],
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def recompute_p12_summary(
    denominator: Mapping[str, Any],
    terminal_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Recompute the frozen estimand from authenticated Phase 7 result bytes."""

    frozen = verify_p12_denominator(denominator)
    jobs = {job["job_id"]: job for job in frozen["jobs"]}
    observed: list[dict[str, str]] = []
    seen: set[str] = set()
    identity_fields = (
        "job_id",
        "object_type",
        "object_id",
        "mr_id",
        "evaluation_input_class",
        "evaluation_input_id",
        "repetition_id",
        "environment_id",
        "job_role",
    )
    for index, candidate in enumerate(terminal_results):
        pair = validate_exact_object(
            dict(candidate), _TERMINAL_P12_SCHEMA, f"terminal_results[{index}]"
        )
        intent = _validate_intent(pair["intent"])
        result = _validate_result(pair["result"], intent)
        job_id = intent["job_id"]
        if job_id not in jobs or job_id in seen:
            raise EvidenceError(
                "E_P12_JOB_SET", "terminal P12 job set differs from denominator"
            )
        if any(intent[field] != jobs[job_id][field] for field in identity_fields):
            raise EvidenceError(
                "E_P12_IDENTITY", "terminal result identity differs from denominator"
            )
        if (
            intent["phase"] != "PHASE_7"
            or result["job_id"] != job_id
            or result["attempt"] != intent["attempt"]
        ):
            raise EvidenceError(
                "E_P12_IDENTITY", "terminal result is not the matching Phase 7 attempt"
            )
        seen.add(job_id)
        observed.append(
            {"job_id": job_id, "scientific_outcome": result["scientific_outcome"]}
        )
    if seen != set(jobs):
        raise EvidenceError(
            "E_P12_JOB_SET", "terminal P12 job set differs from denominator"
        )
    summary = summarize_p12_outcomes(frozen, observed)
    body = {
        key: value for key, value in summary.items() if key != "artifact_sha256"
    }
    body["missingness"] = {
        "SCIENTIFIC_INCONCLUSIVE": body["scientific_inconclusive_count"],
        "INFRASTRUCTURE_UNRESOLVED": body["infrastructure_unresolved_count"],
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def validate_claim_ledger(claims: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a self-hashed, blocked-only ledger bound to frozen authorities."""

    value = validate_exact_object(dict(claims), _CLAIM_LEDGER_SCHEMA, "claims")
    if value["schema_version"] != "p3-claim-evidence-v1":
        raise EvidenceError("E_CLAIM_LEDGER", "claim ledger version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    validate_sha256(value["artifact_sha256"], "claims.artifact_sha256")
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_CLAIM_HASH", "claim ledger self-hash differs")
    validate_sha256(
        value["claim_authority_sha256"], "claims.claim_authority_sha256"
    )
    validate_sha256(value["rq_authority_sha256"], "claims.rq_authority_sha256")
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["claims"]):
        claim = validate_exact_object(
            candidate, _CLAIM_SCHEMA, f"claims.claims[{index}]"
        )
        claim_body = {
            key: item for key, item in claim.items() if key != "artifact_sha256"
        }
        validate_sha256(
            claim["artifact_sha256"], f"claims.claims[{index}].artifact_sha256"
        )
        if claim["artifact_sha256"] != canonical_sha256(claim_body):
            raise EvidenceError("E_CLAIM_HASH", "claim self-hash differs")
        if claim["status"] != "blocked":
            raise EvidenceError("E_CLAIM_STATUS", "all scientific claims must be blocked")
        if not claim["claim_id"]:
            raise EvidenceError("E_CLAIM_SET", "claim ID is empty")
        rqs = claim["rqs"]
        if (
            not rqs
            or rqs != sorted(set(rqs))
            or any(type(rq) is not str or not rq for rq in rqs)
        ):
            raise EvidenceError("E_CLAIM_SET", "claim RQ associations are not canonical")
        references = claim["evidence_references"]
        if (
            not references
            or references != sorted(set(references))
            or any(type(reference) is not str for reference in references)
        ):
            raise EvidenceError(
                "E_CLAIM_EVIDENCE", "claim evidence references are not canonical"
            )
        for reference in references:
            safe_relative_path(reference)
        normalized.append(claim)
    claim_ids = [claim["claim_id"] for claim in normalized]
    if claim_ids != list(dict.fromkeys(claim_ids)):
        raise EvidenceError("E_CLAIM_SET", "claim IDs must be unique")
    return value
