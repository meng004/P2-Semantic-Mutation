#!/usr/bin/env python3
"""One frozen-row P2-C attempt via existing create_intent / write_result."""

from __future__ import annotations

import argparse
import hashlib
import platform
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from p3_v3.run_records import create_intent, write_result  # noqa: E402

EXPECTED_COMMIT = "4444061dde0159a5edd62753fe3cef2d881a308c"
PROTOCOL_SHA256 = (
    "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
)
RECEIPTS_SHA256 = (
    "8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440"
)
WORKLOAD_SHA256 = (
    "db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d"
)
IDS_SHA256 = (
    "e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6"
)
LOCK_SHA256 = (
    "7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f"
)
ARCHIVE_SHA256 = (
    "c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c"
)
PLACEHOLDER_ENV = (
    "396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007"
)
EMPTY_STREAM = hashlib.sha256(b"").hexdigest()
EMPTY_TRACE = "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
PINNED_BEHAVIOR = (
    "72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db"
)
SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EVAL_INPUT_ID = (
    "60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8"
)
RECEIPTS_REL = "data/p3_v3/phase1_frames/receipts.json"
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
EXTRACTED_REL = f"data/p3_v3/p12_intake/extracted/{SNAPSHOT_ID}"
ARCHIVE_REL = f"data/p3_v3/p12_intake/archives/{SNAPSHOT_ID}.tar"
JOB_ID = "p2c-20260819-003"
FIXED_ARGV = [
    "python3",
    "scripts/p3_v3/run_p2c_one_row.py",
    "--root",
    ".",
    "--workload",
    WORKLOAD_REL,
    "--behavior-id",
    PINNED_BEHAVIOR,
    "--jobs-root",
    "data/p3_v3/phase2_profiling/jobs",
    "--job-id",
    JOB_ID,
    "--terminal-output",
    "data/p3_v3/phase2_profiling/row-terminal.json",
]


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("E_PREFLIGHT_GIT", f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _require_clean_baseline(root: Path) -> None:
    head = _git(root, "rev-parse", "HEAD")
    if head != EXPECTED_COMMIT:
        raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")


def _first_executable_subject(receipts: dict) -> dict:
    for row in receipts["subjects"]:
        if row["discovery_status"] == "EXECUTABLE":
            return row
    raise EvidenceError("E_SUBJECT", "no EXECUTABLE subject in receipts")


def _source_tree_present(root: Path) -> bool:
    extracted = root / EXTRACTED_REL
    if extracted.is_dir() and not extracted.is_symlink():
        return True
    archive = root / ARCHIVE_REL
    if not archive.is_file() or archive.is_symlink():
        return False
    if file_sha256(archive) != ARCHIVE_SHA256:
        return False
    extracted.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r") as handle:
        handle.extractall(extracted)
    return extracted.is_dir()


def _environment_sha256() -> str:
    digest = canonical_sha256(
        {
            "dependency_lock_sha256": LOCK_SHA256,
            "domain": "P3-P2C-ONE-ROW-ENV-v1",
            "platform": platform.system(),
            "python": platform.python_version(),
        }
    )
    if digest == PLACEHOLDER_ENV:
        raise EvidenceError("E_ENV", "environment digest collided with placeholder")
    return digest


def main(argv: list[str] | None = None) -> int:
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--behavior-id", required=True)
    parser.add_argument("--jobs-root", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--terminal-output", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.workload != WORKLOAD_REL or args.behavior_id != PINNED_BEHAVIOR:
        raise EvidenceError("E_PINNED_ROW", "invocation is not the pinned row")
    if args.job_id != JOB_ID:
        raise EvidenceError("E_JOB_ID", "job id is not the authorized packet job")

    _require_clean_baseline(root)
    workload_path = root / args.workload
    if file_sha256(workload_path) != WORKLOAD_SHA256:
        raise EvidenceError("E_WORKLOAD", "workload file digest differs")
    workload = read_canonical_json(workload_path)
    if canonical_sha256(workload["selected_behavior_ids"]) != IDS_SHA256:
        raise EvidenceError("E_WORKLOAD", "selected behavior set digest differs")
    if workload["selected_behavior_ids"][0] != PINNED_BEHAVIOR:
        raise EvidenceError("E_PINNED_ROW", "first selected behavior differs")

    receipts_path = root / RECEIPTS_REL
    if file_sha256(receipts_path) != RECEIPTS_SHA256:
        raise EvidenceError("E_RECEIPTS", "receipts digest differs")
    subject = _first_executable_subject(read_canonical_json(receipts_path))
    if subject["neutral_snapshot_id"] != SNAPSHOT_ID:
        raise EvidenceError("E_SUBJECT", "first EXECUTABLE subject differs")

    tree_present = _source_tree_present(root)
    failure_code = (
        "E_PROFILE_NO_PROCESS_ARGV" if tree_present else "E_SOURCE_TREE_ABSENT"
    )

    attempt_dir = root / args.jobs_root / args.job_id / "1"
    intent = {
        "job_id": JOB_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "phase": "PHASE_1",
        "argv": list(FIXED_ARGV),
        "cwd_identity": "github.com/meng004/P3-Semantic-Mutation",
        "environment_sha256": _environment_sha256(),
        "input_sha256": sorted(
            {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
        ),
        "seed": None,
        "timeout_seconds": 60,
        "attempt": 1,
        "object_type": "PROFILING_BEHAVIOR",
        "object_id": PINNED_BEHAVIOR,
        "mr_id": "not-applicable",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": EVAL_INPUT_ID,
        "repetition_id": 1,
        "environment_id": "p2c-one-row-2026-08-19-003",
        "job_role": "PROFILING",
    }
    create_intent(attempt_dir, intent)
    result = {
        "job_id": JOB_ID,
        "attempt": 1,
        "status": "MISSING_WITH_REASON",
        "exit_code": None,
        "stdout_sha256": EMPTY_STREAM,
        "stderr_sha256": EMPTY_STREAM,
        "duration_seconds": time.monotonic() - started,
        "failure_code": failure_code,
        "scientific_outcome": None,
        "call_trace_sha256": EMPTY_TRACE,
        "call_trace_identity": canonical_sha256(
            {
                "job_id": JOB_ID,
                "attempt": 1,
                "behavior_id": PINNED_BEHAVIOR,
                "call_trace_sha256": EMPTY_TRACE,
                "domain": "P3-PROFILING-TRACE-v1",
            }
        ),
    }
    write_result(attempt_dir, result)

    terminal_body = {
        "schema_version": "p3-p2c-one-row-terminal-v1",
        "packet_id": "2026-08-19-003",
        "scientific_target": "P2-C",
        "neutral_snapshot_id": SNAPSHOT_ID,
        "discovery_status": subject["discovery_status"],
        "adapter_id": subject["adapter_id"],
        "behavior_id": PINNED_BEHAVIOR,
        "denominator": "PROFILING_ONE_ROW",
        "formal_denominator_membership": False,
        "claims": "blocked",
        "result_status": result["status"],
        "result_failure_code": result["failure_code"],
        "workload_file_sha256": WORKLOAD_SHA256,
        "selected_behavior_ids_sha256": IDS_SHA256,
    }
    terminal_body["artifact_sha256"] = canonical_sha256(terminal_body)
    write_canonical_json(Path(args.terminal_output), terminal_body, exclusive=True)
    sys.stdout.buffer.write(
        (
            '{"status":"%s","failure_code":"%s","artifact_sha256":"%s"}\n'
            % (
                result["status"],
                result["failure_code"],
                terminal_body["artifact_sha256"],
            )
        ).encode("utf-8")
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        sys.stderr.write(f"{exc}\n")
        raise SystemExit(2)
