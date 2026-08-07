#!/usr/bin/env python3
"""Supplemental R3 Amendment 01 Bootstrap Addendum 01 TDD matrix runner.

stdlib-only CLI:
  --initialize-journal --bootstrap-records PATH --journal PATH
  --phase red|green --manifest PATH --report PATH --journal PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

PARENT_EXECUTION_PLAN_SHA256 = (
    "7adda5c7df3b792ba112e3348d64434d6543d867d339d5e301d2b096119ceac5"
)
BOOTSTRAP_ADDENDUM_PLAN_SHA256 = (
    "7363445ea67618e9f5bb378a0b45eaad07ed4c57f9fcce87323d99a1a6d59c5b"
)
REQUIRED_BRANCH = (
    "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-01-evidence"
)
REQUIRED_AUTHORITY = "31a4a8249f4ba6de12ba92291ab0cd55a65043b4"
REQUIRED_FETCH_ARGV = [
    "git",
    "fetch",
    "--no-tags",
    "origin",
    (
        "refs/heads/codex/phase3-supplemental-r3-ref-isolation-amendment:"
        "refs/remotes/origin/codex/phase3-supplemental-r3-ref-isolation-amendment"
    ),
]
REQUIRED_SWITCH_ARGV = [
    "git",
    "switch",
    "-c",
    REQUIRED_BRANCH,
    REQUIRED_AUTHORITY,
]
FIRST_ARGV = ["git", "rev-parse", "HEAD"]
REQUIRED_RECORD_FIELDS = (
    "sequence",
    "stage",
    "argv",
    "started_at_utc",
    "ended_at_utc",
    "exit_code",
    "stdout_sha256",
    "stderr_sha256",
    "evidence_request",
    "runner_state",
    "parent_execution_plan_sha256",
    "bootstrap_addendum_plan_sha256",
)
FORBIDDEN_TOKENS = (
    "for-each-ref",
    "show-ref",
    "fsck",
)


def _die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def _canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _exclusive_write_bytes(path: str, data: bytes) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags, 0o644)
    try:
        view = memoryview(data)
        written = 0
        while written < len(data):
            written += os.write(fd, view[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _append_jsonl_record(path: str, record: dict[str, Any]) -> None:
    line = (_canonical_dumps(record) + "\n").encode("utf-8")
    fd = os.open(path, os.O_APPEND | os.O_WRONLY)
    try:
        view = memoryview(line)
        written = 0
        while written < len(line):
            written += os.write(fd, view[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _argv_contains_forbidden(argv: list[Any]) -> bool:
    if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
        return True
    if len(argv) >= 2 and argv[0] == "git":
        # git branch -a
        if "branch" in argv and "-a" in argv:
            return True
        # git log --all
        if "log" in argv and "--all" in argv:
            return True
        # git rev-list --all
        if "rev-list" in argv and "--all" in argv:
            return True
        for token in FORBIDDEN_TOKENS:
            if token in argv:
                return True
    # also catch forbidden tokens anywhere in argv strings
    joined = " ".join(argv)
    for token in (
        "for-each-ref",
        "show-ref",
        "branch -a",
        "log --all",
        "rev-list --all",
        "fsck",
    ):
        if token in joined:
            return True
    return False


def _is_switch_to_authority(argv: list[Any]) -> bool:
    return argv == REQUIRED_SWITCH_ARGV


def validate_bootstrap_records(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        _die("bootstrap records must be a non-empty JSON array")

    validated: list[dict[str, Any]] = []
    fetch_count = 0
    switch_count = 0

    for idx, raw in enumerate(records, start=1):
        if not isinstance(raw, dict):
            _die(f"record {idx} is not an object")
        missing = [f for f in REQUIRED_RECORD_FIELDS if f not in raw]
        if missing:
            _die(f"record {idx} missing fields: {', '.join(missing)}")

        sequence = raw["sequence"]
        if sequence != idx:
            _die(f"sequence must be contiguous from 1; expected {idx}, got {sequence!r}")

        argv = raw["argv"]
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            _die(f"record {idx} argv must be a list of strings")

        if raw["parent_execution_plan_sha256"] != PARENT_EXECUTION_PLAN_SHA256:
            _die(f"record {idx} parent_execution_plan_sha256 mismatch")
        if raw["bootstrap_addendum_plan_sha256"] != BOOTSTRAP_ADDENDUM_PLAN_SHA256:
            _die(f"record {idx} bootstrap_addendum_plan_sha256 mismatch")
        if raw["evidence_request"] is not False:
            _die(f"record {idx} evidence_request must be false")
        if _argv_contains_forbidden(argv):
            _die(f"record {idx} contains forbidden command: {argv!r}")

        if argv == REQUIRED_FETCH_ARGV:
            fetch_count += 1
        if _is_switch_to_authority(argv):
            switch_count += 1

        validated.append(raw)

    first = validated[0]
    if first["argv"] != FIRST_ARGV:
        _die(f"first argv must be {FIRST_ARGV!r}")
    if first["exit_code"] != 0:
        _die("first record exit_code must be 0")

    if fetch_count != 1:
        _die(f"expected exactly one authorization fetch argv, found {fetch_count}")
    if switch_count != 1:
        _die(
            "expected exactly one switch to "
            f"{REQUIRED_BRANCH!r} at {REQUIRED_AUTHORITY!r}, found {switch_count}"
        )

    if validated[-1]["stage"] != "task1_baseline_hashes":
        _die("bootstrap records must end with stage task1_baseline_hashes")

    return validated


def cmd_initialize_journal(bootstrap_records_path: str, journal_path: str) -> int:
    try:
        payload = json.loads(open(bootstrap_records_path, "r", encoding="utf-8").read())
    except (OSError, json.JSONDecodeError) as exc:
        _die(f"failed to load bootstrap records: {exc}")

    records = validate_bootstrap_records(payload)

    if os.path.exists(journal_path):
        _die(f"journal already exists: {journal_path}")

    state_path = f"{journal_path}.state.json"
    if os.path.exists(state_path):
        _die(f"journal state already exists: {state_path}")

    lines = [(_canonical_dumps(rec) + "\n").encode("utf-8") for rec in records]
    body = b"".join(lines)
    try:
        _exclusive_write_bytes(journal_path, body)
    except FileExistsError:
        _die(f"journal already exists: {journal_path}")
    except OSError as exc:
        _die(f"failed to create journal: {exc}")

    state = {
        "shutdown_runner_armed": False,
        "payload_tree_published": False,
        "terminal": False,
        "evidence_request_count": 0,
    }
    state_bytes = (_canonical_dumps(state) + "\n").encode("utf-8")
    try:
        _exclusive_write_bytes(state_path, state_bytes)
    except FileExistsError:
        _die(f"journal state already exists: {state_path}")
    except OSError as exc:
        _die(f"failed to create journal state: {exc}")

    return 0


def _parse_collected_count(text: str) -> int | None:
    match = re.search(r"collected\s+(\d+)\s+items?", text)
    if match:
        return int(match.group(1))
    return None


def _summary_count(text: str, label: str) -> int:
    match = re.search(rf"(\d+)\s+{label}\b", text)
    return int(match.group(1)) if match else 0


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", ".."))


def _run_pytest_node(node_id: str) -> tuple[list[str], int, bytes, bytes]:
    argv = ["python3", "-m", "pytest", node_id, "--maxfail=1", "-q"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    proc = subprocess.run(
        argv,
        cwd=_repo_root(),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    return argv, proc.returncode, proc.stdout, proc.stderr


def _reject_red_masking(combined: str) -> str | None:
    lowered = combined.lower()
    if "error collecting" in lowered or "errors during collection" in lowered:
        return "collection ERROR"
    if re.search(r"\berror\b", combined, re.I) and "failed" not in lowered:
        # collection / import ERROR without a failed test
        if "ERROR:" in combined or "==== ERRORS ====" in combined:
            return "collection/import ERROR"
    if _summary_count(combined, "passed") > 0 or re.search(r"\bPASSED\b", combined):
        return "unexpected PASS"
    if _summary_count(combined, "skipped") > 0 or re.search(r"\bSKIPPED\b", combined):
        return "unexpected SKIP"
    if _summary_count(combined, "xfailed") > 0 or re.search(r"\bXFAIL\b", combined):
        return "unexpected XFAIL"
    if "no tests ran" in lowered:
        return "no tests ran"
    return None


def _evaluate_red(
    node_id: str,
    red_signature: str,
    exit_code: int,
    stdout: bytes,
    stderr: bytes,
) -> None:
    combined = stdout.decode("utf-8", errors="replace") + stderr.decode(
        "utf-8", errors="replace"
    )
    collected = _parse_collected_count(combined)
    if collected is None:
        _die(f"RED {node_id}: could not parse collected test count")
    if collected != 1:
        _die(f"RED {node_id}: expected exactly one collected test, got {collected}")

    mask = _reject_red_masking(combined)
    if mask:
        _die(f"RED {node_id}: {mask}")

    if exit_code == 0:
        _die(f"RED {node_id}: pytest exited 0 (expected nonzero FAIL)")

    failed = _summary_count(combined, "failed")
    if failed != 1 and "FAILED" not in combined:
        _die(f"RED {node_id}: expected exactly one FAIL")

    if red_signature not in combined:
        _die(f"RED {node_id}: missing red_signature {red_signature!r}")


def _evaluate_green(node_id: str, exit_code: int, stdout: bytes, stderr: bytes) -> None:
    combined = stdout.decode("utf-8", errors="replace") + stderr.decode(
        "utf-8", errors="replace"
    )
    if exit_code != 0:
        _die(f"GREEN {node_id}: pytest exited {exit_code}, expected 0")
    if _summary_count(combined, "failed") > 0 or "FAILED" in combined:
        _die(f"GREEN {node_id}: unexpected failed tests")
    if _summary_count(combined, "passed") < 1 and "passed" not in combined:
        _die(f"GREEN {node_id}: expected passed summary")
    if _summary_count(combined, "skipped") > 0 or "SKIPPED" in combined:
        _die(f"GREEN {node_id}: unexpected SKIP")
    if _summary_count(combined, "xfailed") > 0 or "XFAIL" in combined:
        _die(f"GREEN {node_id}: unexpected XFAIL")


def _next_journal_sequence(journal_path: str) -> int:
    if not os.path.exists(journal_path):
        _die(f"journal does not exist: {journal_path}")
    last = 0
    with open(journal_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            seq = int(rec["sequence"])
            if seq > last:
                last = seq
    return last + 1


def cmd_phase(phase: str, manifest_path: str, report_path: str, journal_path: str) -> int:
    if phase not in ("red", "green"):
        _die("--phase must be red or green")

    try:
        manifest = json.loads(open(manifest_path, "r", encoding="utf-8").read())
    except (OSError, json.JSONDecodeError) as exc:
        _die(f"failed to load manifest: {exc}")

    if not isinstance(manifest, dict) or "nodes" not in manifest:
        _die("manifest must be an object with a nodes array")
    nodes = manifest["nodes"]
    if not isinstance(nodes, list) or not nodes:
        _die("manifest.nodes must be a non-empty array")

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    started = _utc_now()

    for raw in nodes:
        if not isinstance(raw, dict):
            _die("each manifest node must be an object")
        node_id = raw.get("node_id")
        red_signature = raw.get("red_signature")
        if not isinstance(node_id, str) or not node_id:
            _die("node_id must be a non-empty string")
        if node_id in seen:
            _die(f"duplicate node_id: {node_id}")
        seen.add(node_id)
        if phase == "red" and (not isinstance(red_signature, str) or not red_signature):
            _die(f"node {node_id}: red_signature required for red phase")

        argv, exit_code, stdout, stderr = _run_pytest_node(node_id)
        stdout_sha = _sha256_bytes(stdout)
        stderr_sha = _sha256_bytes(stderr)

        if phase == "red":
            _evaluate_red(node_id, str(red_signature), exit_code, stdout, stderr)
            outcome = "red_fail"
        else:
            _evaluate_green(node_id, exit_code, stdout, stderr)
            outcome = "green_pass"

        entry: dict[str, Any] = {
            "argv": argv,
            "exit_code": exit_code,
            "node_id": node_id,
            "outcome": outcome,
            "red_signature": red_signature if isinstance(red_signature, str) else "",
            "stderr_sha256": stderr_sha,
            "stdout_sha256": stdout_sha,
        }
        results.append(entry)

    ended = _utc_now()
    report = {
        "evidence_request_count": 0,
        "nodes": results,
        "phase": phase,
    }
    report_bytes = (_canonical_dumps(report) + "\n").encode("utf-8")
    try:
        with open(report_path, "wb") as handle:
            handle.write(report_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        _die(f"failed to write report: {exc}")

    sequence = _next_journal_sequence(journal_path)
    journal_record = {
        "argv": list(sys.argv),
        "ended_at_utc": ended,
        "evidence_request": False,
        "exit_code": 0,
        "runner_state": f"tdd_matrix_{phase}",
        "sequence": sequence,
        "stage": f"tdd_matrix_{phase}",
        "started_at_utc": started,
        "stderr_sha256": _sha256_bytes(b""),
        "stdout_sha256": _sha256_bytes(report_bytes),
    }
    try:
        _append_jsonl_record(journal_path, journal_record)
    except OSError as exc:
        _die(f"failed to append journal: {exc}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Supplemental R3 Bootstrap Addendum 01 TDD matrix runner"
    )
    parser.add_argument(
        "--initialize-journal",
        action="store_true",
        help="Validate bootstrap records and exclusive-create journal + state sidecar",
    )
    parser.add_argument("--bootstrap-records", help="Path to bootstrap records JSON array")
    parser.add_argument(
        "--phase",
        choices=("red", "green"),
        help="Run node-by-node RED or GREEN matrix",
    )
    parser.add_argument("--manifest", help="Path to TDD nodes manifest JSON")
    parser.add_argument("--report", help="Path to write canonical phase report JSON")
    parser.add_argument("--journal", required=True, help="Path to JSONL command journal")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.initialize_journal:
        if args.phase is not None:
            _die("cannot combine --initialize-journal with --phase")
        if not args.bootstrap_records:
            _die("--bootstrap-records is required with --initialize-journal")
        return cmd_initialize_journal(args.bootstrap_records, args.journal)

    if args.phase is None:
        _die("either --initialize-journal or --phase is required")
    if not args.manifest:
        _die("--manifest is required with --phase")
    if not args.report:
        _die("--report is required with --phase")
    return cmd_phase(args.phase, args.manifest, args.report, args.journal)


if __name__ == "__main__":
    raise SystemExit(main())
