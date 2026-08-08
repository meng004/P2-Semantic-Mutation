#!/usr/bin/env python3
"""Terminal history and handoff binding checks for Supplemental R3."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence


class GateError(RuntimeError):
    pass


HANDOFF_PATH = "data/external_slice/supplemental_r3/HANDOFF_SUPPLEMENTAL_R3.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
FULL_SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_QUOTAS = {
    "cornellius-gp/gpytorch": 2,
    "jonathf/chaospy": 3,
    "SALib/SALib": 3,
}
PAYLOAD_MANIFEST = "PAYLOAD_MANIFEST_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"
PAYLOAD_PREFIX = "data/external_slice/supplemental_r3/"
VM_SEAL_PATH = "data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json"
BUNDLE_MANIFEST_PATH = (
    "data/external_slice/supplemental_r3/"
    "EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"
)
EVIDENCE_BRANCH = "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence"
PAYLOAD_COMMIT_COMMAND = (
    "git", "commit", "-m", "evidence(external): publish Supplemental R3 payload"
)
HANDOFF_COMMIT_COMMAND = (
    "git", "commit", "-m", "evidence(external): add Supplemental R3 handoff"
)
PUSH_COMMAND = ("git", "push", "-u", "origin", EVIDENCE_BRANCH)


def _load_common():
    path = Path(__file__).with_name("supplemental_r3_common.py")
    spec = importlib.util.spec_from_file_location("_supplemental_r3_common_handoff", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load supplemental_r3_common")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_common()


def _load_admission():
    path = Path(__file__).with_name("check_supplemental_r3_admission.py")
    spec = importlib.util.spec_from_file_location("_supplemental_r3_admission_handoff", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load supplemental_r3 admission")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_admission = _load_admission()


def _manifest_path(root: Path) -> Path:
    return Path(root) / PAYLOAD_PREFIX / PAYLOAD_MANIFEST


def verify_direct_child_history(
    *,
    payload_commit: str,
    handoff_commit: str,
    handoff_parents: Sequence[str],
    changed_paths: Sequence[str],
) -> None:
    if not FULL_SHA.fullmatch(payload_commit) or not FULL_SHA.fullmatch(handoff_commit):
        raise GateError("handoff_history")
    if list(handoff_parents) != [payload_commit] or list(changed_paths) != [HANDOFF_PATH]:
        raise GateError("handoff_history")


def verify_handoff_bindings(handoff: dict[str, Any]) -> None:
    if handoff.get("protocol") != "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03":
        raise GateError("protocol")
    if handoff.get("amendment_id") != "AMENDMENT_01_REF_ISOLATION":
        raise GateError("amendment_id")
    if handoff.get("bootstrap_addendum_id") != "BOOTSTRAP_EXECUTION_ADDENDUM_03":
        raise GateError("bootstrap_addendum_id")
    plans = handoff.get("plan_sha256")
    if not isinstance(plans, list) or len(plans) != 4 or not all(FULL_SHA256.fullmatch(str(item)) for item in plans):
        raise GateError("plan_lineage")
    for key in ("bundle_commit", "bundle_tree"):
        if not FULL_SHA.fullmatch(str(handoff.get(key, ""))):
            raise GateError("bundle_binding")
    if not FULL_SHA.fullmatch(str(handoff.get("payload_commit", ""))):
        raise GateError("payload_binding")
    for key in (
        "bundle_manifest_sha256", "spool_sha256", "design_sha256",
        "pre_network_seal_sha256", "pre_network_journal_prefix_sha256", "journal_sha256",
        "vm_green_report_sha256",
    ):
        if not FULL_SHA256.fullmatch(str(handoff.get(key, ""))):
            raise GateError("bundle_binding")
    if not FULL_SHA.fullmatch(str(handoff.get("pre_network_seal_commit", ""))):
        raise GateError("pre_network_seal_binding")
    if (
        handoff.get("pre_network_evidence_request_count") != 0
        or not isinstance(handoff.get("evidence_request_count"), int)
        or handoff.get("evidence_request_count", 0) <= 0
        or not isinstance(handoff.get("pre_network_journal_record_count"), int)
        or not isinstance(handoff.get("journal_record_count"), int)
    ):
        raise GateError("journal_binding")
    vm_green = handoff.get("vm_green")
    if (
        not isinstance(vm_green, dict)
        or vm_green.get("evidence_request_count") != 0
        or not isinstance(vm_green.get("node_count"), int)
        or vm_green.get("node_count", 0) <= 0
        or not isinstance(vm_green.get("full_suite"), dict)
        or vm_green["full_suite"].get("passed", 0) <= 0
        or handoff.get("environment_seal_commit_command")
        != ["git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"]
    ):
        raise GateError("vm_green_binding")
    if handoff.get("verdict") != (
        "SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03_"
        "EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT"
    ):
        raise GateError("research_evidence_verdict")
    if handoff.get("research_evidence_boundary") != {
        "candidate_evidence_only": True,
        "manuscript_claims_unmodified": True,
        "requires_separate_local_desktop_evidence_audit_pass": True,
    }:
        raise GateError("research_evidence_boundary")
    if handoff.get("quota_results") != EXPECTED_QUOTAS:
        raise GateError("quota_results")
    verify_terminal_commands(handoff.get("terminal_commands", []))


def _read_payload_commit(*, root: Path, journal: Path, manifest: dict[str, Any]) -> str:
    runner = _common.TerminalCommandRunner(Path(journal))
    root_text = str(Path(root))
    head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
    head = head_raw.decode("ascii").strip()
    history_raw, _ = runner.run([
        "git", "-C", root_text, "rev-list", "--parents", "-n", "1", head
    ])
    changed_raw, _ = runner.run([
        "git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", head
    ])
    changed = [line for line in changed_raw.decode("utf-8").splitlines() if line]
    expected = {PAYLOAD_PREFIX + path for path in manifest["candidate_file_sha256"]}
    expected.add(PAYLOAD_PREFIX + PAYLOAD_MANIFEST)
    if history_raw.decode("ascii").strip().split() != [head, manifest.get("pre_network_seal_commit")]:
        raise GateError("payload_history")
    if set(changed) != expected or len(changed) != len(expected):
        raise GateError("payload_history")
    committed_raw, _ = runner.run([
        "git", "-C", root_text, "show", f"HEAD:{PAYLOAD_PREFIX}{PAYLOAD_MANIFEST}"
    ])
    if committed_raw != _manifest_path(Path(root)).read_bytes():
        raise GateError("payload_committed_bytes")
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"
    ])
    if status_raw:
        raise GateError("payload_worktree_drift")
    return head


def _verify_journal_prefix(
    *, journal: Path, record_count: int, expected_sha256: str, label: str
) -> None:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    if record_count <= 0 or record_count > len(lines):
        raise GateError(f"{label}_journal_count")
    prefix = b"".join(lines[:record_count])
    if hashlib.sha256(prefix).hexdigest() != expected_sha256:
        raise GateError(f"{label}_journal_sha256")


def handle_build_handoff(
    *, root: Path, authority: str, journal: Path, output: Path
) -> int:
    if not FULL_SHA.fullmatch(authority):
        raise GateError("authority_sha")
    if Path(output) != Path(root) / HANDOFF_PATH:
        raise GateError("handoff_output_path")
    manifest_path = _manifest_path(Path(root))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"payload_manifest: {exc}") from exc
    try:
        _admission.verify_payload_manifest_exact(
            root=Path(root),
            payload_root=manifest_path.parent,
            authority=authority,
            journal=Path(journal),
        )
    except Exception as exc:
        raise GateError(f"payload_manifest_binding: {exc}") from exc
    payload_commit = _read_payload_commit(root=Path(root), journal=Path(journal), manifest=manifest)
    handoff = dict(manifest)
    handoff.update(
        {
            "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
            "amendment_id": "AMENDMENT_01_REF_ISOLATION",
            "bootstrap_addendum_id": "BOOTSTRAP_EXECUTION_ADDENDUM_03",
            "authority": authority,
            "payload_commit": payload_commit,
        }
    )
    verify_handoff_bindings(handoff)
    runner = _common.TerminalCommandRunner(Path(journal))
    operation_key = runner.begin_operation(
        "build_handoff", {"output": str(Path(output)), "payload_commit": payload_commit}
    )
    _common.atomic_write_bytes(Path(output), _common.canonical_json_bytes(handoff) + b"\n")
    runner.complete_operation(
        operation_key, {"sha256": hashlib.sha256(Path(output).read_bytes()).hexdigest()}
    )
    return 0


def _verify_handoff_git_history(
    *, root: Path, journal: Path, payload_commit: str, handoff_path: Path
) -> None:
    runner = _common.TerminalCommandRunner(Path(journal))
    root_text = str(Path(root))
    head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
    head = head_raw.decode("ascii").strip()
    history_raw, _ = runner.run([
        "git", "-C", root_text, "rev-list", "--parents", "-n", "1", head
    ])
    changed_raw, _ = runner.run([
        "git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", head
    ])
    verify_direct_child_history(
        payload_commit=payload_commit,
        handoff_commit=head,
        handoff_parents=history_raw.decode("ascii").strip().split()[1:],
        changed_paths=[line for line in changed_raw.decode("utf-8").splitlines() if line],
    )
    committed_raw, _ = runner.run(["git", "-C", root_text, "show", f"HEAD:{HANDOFF_PATH}"])
    if committed_raw != Path(handoff_path).read_bytes():
        raise GateError("handoff_committed_bytes")
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"
    ])
    if status_raw:
        raise GateError("handoff_worktree_drift")


def handle_verify_handoff(*, root: Path, handoff: Path, authority: str, journal: Path) -> int:
    raw = Path(handoff).read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"handoff_json: {exc}") from exc
    if raw != _common.canonical_json_bytes(payload) + b"\n":
        raise GateError("handoff_not_canonical")
    if payload.get("authority") != authority:
        raise GateError("authority_binding")
    verify_handoff_bindings(payload)
    try:
        manifest = json.loads(_manifest_path(Path(root)).read_text(encoding="utf-8"))
        seal_path = Path(root) / VM_SEAL_PATH
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
        bundle_path = Path(root) / BUNDLE_MANIFEST_PATH
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"lineage_json: {exc}") from exc
    candidate_hashes = manifest.get("candidate_file_sha256")
    if not isinstance(candidate_hashes, dict) or not candidate_hashes:
        raise GateError("handoff_candidate_paths")
    _common.verify_batch3_active_paths(
        root=Path(root),
        paths=[
            Path(handoff),
            _manifest_path(Path(root)),
            *[
                Path(root) / PAYLOAD_PREFIX / relative
                for relative in sorted(candidate_hashes)
            ],
        ],
    )
    try:
        _admission.verify_payload_manifest_exact(
            root=Path(root),
            payload_root=_manifest_path(Path(root)).parent,
            authority=authority,
            journal=Path(journal),
        )
    except Exception as exc:
        raise GateError(f"payload_manifest_binding: {exc}") from exc
    inherited = set(manifest)
    additions = {"amendment_id", "bootstrap_addendum_id", "payload_commit"}
    if set(payload) != inherited | additions or any(
        payload.get(key) != value for key, value in manifest.items()
    ):
        raise GateError("handoff_payload_projection")
    if (
        hashlib.sha256(bundle_path.read_bytes()).hexdigest() != payload["bundle_manifest_sha256"]
        or hashlib.sha256(seal_path.read_bytes()).hexdigest() != payload["pre_network_seal_sha256"]
        or bundle.get("authority") != authority
        or bundle.get("design_sha256") != payload["design_sha256"]
        or bundle.get("parent_plan_sha256") != payload["plan_sha256"][:3]
        or seal.get("plan_sha256") != payload["plan_sha256"]
        or seal.get("bundle_commit") != payload["bundle_commit"]
        or seal.get("bundle_tree") != payload["bundle_tree"]
        or seal.get("bundle_manifest_sha256") != payload["bundle_manifest_sha256"]
        or seal.get("design_sha256") != payload["design_sha256"]
        or seal.get("authority") != authority
        or seal.get("spool_sha256") != payload["spool_sha256"]
        or seal.get("vm_green_report_sha256") != payload["vm_green_report_sha256"]
        or seal.get("vm_green") != payload["vm_green"]
        or seal.get("environment_seal_commit_command")
        != payload["environment_seal_commit_command"]
    ):
        raise GateError("handoff_lineage_binding")
    _verify_journal_prefix(
        journal=Path(journal),
        record_count=payload["pre_network_journal_record_count"],
        expected_sha256=payload["pre_network_journal_prefix_sha256"],
        label="pre_network",
    )
    _verify_journal_prefix(
        journal=Path(journal),
        record_count=payload["journal_record_count"],
        expected_sha256=payload["journal_sha256"],
        label="acquisition",
    )
    _verify_handoff_git_history(
        root=Path(root), journal=Path(journal), payload_commit=payload["payload_commit"], handoff_path=Path(handoff)
    )
    return 0


def verify_terminal_commands(commands: Sequence[Sequence[str]]) -> None:
    values = [list(command) for command in commands]
    expected = [
        list(PAYLOAD_COMMIT_COMMAND),
        list(HANDOFF_COMMIT_COMMAND),
        list(PUSH_COMMAND),
    ]
    if values != expected:
        raise GateError("terminal_commands")
    flattened = " ".join(part for command in values for part in command).casefold()
    if any(token in flattened for token in ("gh pr", " merge", "readiness", "canonical_freeze", " r8 ")):
        raise GateError("terminal_commands")


def _load_push_static_lineage(
    *, root: Path, journal: Path
) -> tuple[dict[str, Any], bytes]:
    handoff_path = Path(root) / HANDOFF_PATH
    manifest_path = _manifest_path(Path(root))
    seal_path = Path(root) / VM_SEAL_PATH
    bundle_path = Path(root) / BUNDLE_MANIFEST_PATH
    try:
        handoff_raw = handoff_path.read_bytes()
        handoff = json.loads(handoff_raw.decode("utf-8"))
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw.decode("utf-8"))
        seal_raw = seal_path.read_bytes()
        seal = json.loads(seal_raw.decode("utf-8"))
        bundle_raw = bundle_path.read_bytes()
        bundle = json.loads(bundle_raw.decode("utf-8"))
    except Exception as exc:
        raise GateError(f"push_static_json: {exc}") from exc
    if any(
        raw != _common.canonical_json_bytes(value) + b"\n"
        for raw, value in (
            (handoff_raw, handoff), (manifest_raw, manifest),
            (seal_raw, seal), (bundle_raw, bundle),
        )
    ):
        raise GateError("push_static_canonical")
    verify_handoff_bindings(handoff)
    if (
        set(handoff) != set(manifest) | {
            "amendment_id", "bootstrap_addendum_id", "payload_commit"
        }
        or any(handoff.get(key) != value for key, value in manifest.items())
        or hashlib.sha256(bundle_raw).hexdigest() != handoff["bundle_manifest_sha256"]
        or hashlib.sha256(seal_raw).hexdigest() != handoff["pre_network_seal_sha256"]
        or bundle.get("authority") != handoff.get("authority")
        or bundle.get("design_sha256") != handoff.get("design_sha256")
        or bundle.get("parent_plan_sha256") != handoff.get("plan_sha256", [])[:3]
        or seal.get("plan_sha256") != handoff.get("plan_sha256")
        or seal.get("bundle_commit") != handoff.get("bundle_commit")
        or seal.get("bundle_tree") != handoff.get("bundle_tree")
        or seal.get("bundle_manifest_sha256") != handoff.get("bundle_manifest_sha256")
        or seal.get("authority") != handoff.get("authority")
    ):
        raise GateError("push_static_lineage")
    _verify_journal_prefix(
        journal=Path(journal),
        record_count=handoff["pre_network_journal_record_count"],
        expected_sha256=handoff["pre_network_journal_prefix_sha256"],
        label="pre_network",
    )
    _verify_journal_prefix(
        journal=Path(journal),
        record_count=handoff["journal_record_count"],
        expected_sha256=handoff["journal_sha256"],
        label="acquisition",
    )
    _admission._verify_environment_journal_provenance(
        root=Path(root),
        journal=Path(journal),
        seal=seal,
        bundle=bundle,
        seal_sha256=hashlib.sha256(seal_raw).hexdigest(),
        seal_raw=seal_raw,
    )
    return handoff, handoff_raw


def _direct_git_bytes(root: Path, *args: str) -> bytes:
    if not (Path(root) / ".git").exists():
        raise GateError("push_git_repository")
    proc = subprocess.run(
        ["git", "-C", str(Path(root)), *args],
        capture_output=True,
        check=False,
        shell=False,
    )
    if proc.returncode != 0 or proc.stderr:
        raise GateError(f"push_git_read: {list(args)!r}")
    return proc.stdout


def _load_push_journal(journal: Path) -> tuple[list[bytes], list[dict[str, Any]]]:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            record = json.loads(line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"push_journal_json: {exc}") from exc
        if line != _common.canonical_json_bytes(record) + b"\n":
            raise GateError("push_journal_canonical")
        records.append(record)
    if [row.get("sequence") for row in records] != list(range(1, len(records) + 1)):
        raise GateError("push_journal_terminal")
    return lines, records


def _verify_push_handoff_tail(
    *, root: Path, records: Sequence[dict[str, Any]], handoff: dict[str, Any],
    handoff_raw: bytes, handoff_commit: str, tail_end: int,
) -> None:
    payload_commit = str(handoff.get("payload_commit", ""))
    root_text = str(Path(root))
    expected_tail = [
        (["git", "-C", root_text, "rev-parse", "HEAD"], (handoff_commit + "\n").encode("ascii")),
        (["git", "-C", root_text, "rev-list", "--parents", "-n", "1", handoff_commit], (handoff_commit + " " + payload_commit + "\n").encode("ascii")),
        (["git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", handoff_commit], (HANDOFF_PATH + "\n").encode("utf-8")),
        (["git", "-C", root_text, "show", f"HEAD:{HANDOFF_PATH}"], handoff_raw),
        (["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"], b""),
    ]
    actual_tail = list(records[tail_end - 5:tail_end])
    if len(actual_tail) != 5:
        raise GateError("push_journal_terminal")
    for record, (expected_argv, expected_stdout) in zip(
        actual_tail, expected_tail, strict=True
    ):
        if (
            record.get("stage") != "command"
            or record.get("argv") != expected_argv
            or record.get("exit_code") != 0
            or record.get("stdout_sha256") != hashlib.sha256(expected_stdout).hexdigest()
            or record.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
            or record.get("evidence_request") is not False
            or record.get("runner_state") != "active"
        ):
            raise GateError("push_journal_terminal")


def _verify_direct_handoff_git(
    *, root: Path, handoff: dict[str, Any], handoff_raw: bytes,
    handoff_commit: str,
) -> None:
    payload_commit = str(handoff.get("payload_commit", ""))
    head = _direct_git_bytes(Path(root), "rev-parse", "HEAD").decode("ascii").strip()
    parents = _direct_git_bytes(
        Path(root), "rev-list", "--parents", "-n", "1", handoff_commit
    ).decode("ascii").strip().split()
    changed = _direct_git_bytes(
        Path(root), "diff-tree", "--no-commit-id", "--name-only", "-r",
        handoff_commit,
    ).decode("utf-8").splitlines()
    committed = _direct_git_bytes(Path(root), "show", f"HEAD:{HANDOFF_PATH}")
    status = _direct_git_bytes(
        Path(root), "status", "--porcelain=v1", "--untracked-files=all"
    )
    if (
        head != handoff_commit
        or parents != [handoff_commit, payload_commit]
        or changed != [HANDOFF_PATH]
        or committed != handoff_raw
        or status
    ):
        raise GateError("push_git_handoff")


def _run_push_git_preflight(
    *, root: Path, journal: Path, handoff: dict[str, Any], handoff_raw: bytes,
    handoff_commit: str,
) -> tuple[Any, dict[str, Any]]:
    runner = _common.TerminalCommandRunner(Path(journal))
    root_text = str(Path(root))
    payload_commit = str(handoff.get("payload_commit", ""))
    start_sequence = runner.sequence + 1

    def checked(argv: list[str], expected_stdout: bytes, label: str) -> None:
        stdout, stderr = runner.run(argv)
        if stdout != expected_stdout or stderr:
            runner.fail_invariant("push_preflight", label)
            raise GateError(f"push_preflight: {label}")

    checked(
        ["git", "-C", root_text, "rev-parse", "HEAD"],
        (handoff_commit + "\n").encode("ascii"), "head",
    )
    checked(
        ["git", "-C", root_text, "rev-list", "--parents", "-n", "1", handoff_commit],
        (handoff_commit + " " + payload_commit + "\n").encode("ascii"),
        "parent",
    )
    checked(
        ["git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", handoff_commit],
        (HANDOFF_PATH + "\n").encode("utf-8"), "changed_path",
    )
    checked(
        ["git", "-C", root_text, "show", f"HEAD:{HANDOFF_PATH}"],
        handoff_raw, "committed_bytes",
    )
    checked(
        ["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"],
        b"", "clean_status",
    )
    _common.verify_batch3_head_ancestry(root=Path(root), runner=runner)
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    end_sequence = runner.sequence
    segment = b"".join(lines[start_sequence - 1:end_sequence])
    if end_sequence - start_sequence + 1 != 6:
        runner.fail_invariant("push_preflight", "record_count")
        raise GateError("push_preflight: record_count")
    return runner, {
        "preflight_command_record_start": start_sequence,
        "preflight_command_record_end": end_sequence,
        "preflight_command_record_count": 6,
        "preflight_command_sha256": hashlib.sha256(segment).hexdigest(),
        "pre_push_journal_record_count": end_sequence,
        "pre_push_journal_sha256": hashlib.sha256(b"".join(lines[:end_sequence])).hexdigest(),
    }


def _push_preflight(
    *, root: Path, journal: Path, handoff_commit: str
) -> tuple[dict[str, Any], str, Any]:
    if not FULL_SHA.fullmatch(handoff_commit):
        raise GateError("push_handoff_commit")
    handoff, handoff_raw = _load_push_static_lineage(root=Path(root), journal=Path(journal))
    _, records = _load_push_journal(Path(journal))
    _verify_push_handoff_tail(
        root=Path(root), records=records, handoff=handoff,
        handoff_raw=handoff_raw, handoff_commit=handoff_commit,
        tail_end=len(records),
    )
    runner, preflight_state = _run_push_git_preflight(
        root=Path(root), journal=Path(journal), handoff=handoff,
        handoff_raw=handoff_raw,
        handoff_commit=handoff_commit,
    )
    return handoff, _push_preflight_digest(
        handoff=handoff, handoff_raw=handoff_raw,
        handoff_commit=handoff_commit,
        preflight_state=preflight_state,
    ), runner


def _push_preflight_digest(
    *, handoff: dict[str, Any], handoff_raw: bytes, handoff_commit: str,
    preflight_state: dict[str, Any],
) -> str:
    projection = {
        "handoff_commit": handoff_commit,
        "payload_commit": handoff["payload_commit"],
        "handoff_sha256": hashlib.sha256(handoff_raw).hexdigest(),
        "pre_network_journal_prefix_sha256": handoff["pre_network_journal_prefix_sha256"],
        "pre_network_journal_record_count": handoff["pre_network_journal_record_count"],
        "journal_sha256": handoff["journal_sha256"],
        "journal_record_count": handoff["journal_record_count"],
        **preflight_state,
    }
    return hashlib.sha256(_common.canonical_json_bytes(projection)).hexdigest()


def handle_push_once(
    *, root: Path, journal: Path, handoff: Path, handoff_commit: str
) -> int:
    if Path(handoff) != Path(root) / HANDOFF_PATH:
        raise GateError("push_handoff_path")
    payload, preflight_sha256, runner = _push_preflight(
        root=Path(root), journal=Path(journal), handoff_commit=handoff_commit
    )
    stdout, stderr = runner.run(
        list(PUSH_COMMAND),
        push_handoff_commit=handoff_commit,
        push_preflight_sha256=preflight_sha256,
    )
    sys.stdout.buffer.write(stdout)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(stderr)
    sys.stderr.buffer.flush()
    return 0


def handle_verify_push_journal(*, root: Path, journal: Path) -> int:
    lines, records = _load_push_journal(Path(journal))
    if len(records) < 8:
        raise GateError("push_journal_terminal")
    push_intents = [row for row in records if row.get("stage") == "push_intent"]
    push_completions = [row for row in records if row.get("stage") == "push_completion"]
    if len(push_intents) != 1 or len(push_completions) != 1:
        raise GateError("push_journal_terminal")
    intent, completion = records[-2:]
    if intent is not push_intents[0] or completion is not push_completions[0]:
        raise GateError("push_journal_terminal")
    handoff_commit = intent.get("handoff_commit")
    preflight_sha256 = intent.get("preflight_sha256")
    push_key = intent.get("push_key")
    prefix_lines = lines[:-2]
    if (
        not FULL_SHA.fullmatch(str(handoff_commit or ""))
        or intent.get("argv") != list(PUSH_COMMAND)
        or intent.get("runner_state") != "pending"
        or intent.get("exit_code") is not None
        or intent.get("evidence_request") is not False
        or intent.get("pre_push_journal_record_count") != len(prefix_lines)
        or intent.get("pre_push_journal_sha256")
        != hashlib.sha256(b"".join(prefix_lines)).hexdigest()
        or not isinstance(push_key, str)
        or completion.get("push_key") != push_key
        or completion.get("handoff_commit") != handoff_commit
        or completion.get("preflight_sha256") != preflight_sha256
        or completion.get("argv") != list(PUSH_COMMAND)
        or completion.get("exit_code") != 0
        or completion.get("evidence_request") is not False
        or completion.get("runner_state") != "success_closed"
    ):
        raise GateError("push_journal_terminal")
    handoff, handoff_raw = _load_push_static_lineage(
        root=Path(root), journal=Path(journal)
    )
    preflight_tail = records[-8:-2]
    preflight_state = {
        "preflight_command_record_start": preflight_tail[0]["sequence"],
        "preflight_command_record_end": preflight_tail[-1]["sequence"],
        "preflight_command_record_count": len(preflight_tail),
        "preflight_command_sha256": hashlib.sha256(b"".join(lines[-8:-2])).hexdigest(),
        "pre_push_journal_record_count": intent.get("pre_push_journal_record_count"),
        "pre_push_journal_sha256": intent.get("pre_push_journal_sha256"),
    }
    ancestry_stdout = _direct_git_bytes(Path(root), "rev-list", "HEAD")
    deny = _common.load_authority_contract(Path(root))["batch3_deny_sha"]
    ancestry = ancestry_stdout.decode("ascii").splitlines()
    ancestry_record = preflight_tail[-1]
    if (
        not ancestry
        or deny in ancestry
        or any(not FULL_SHA.fullmatch(value) for value in ancestry)
        or ancestry_record.get("stage") != "command"
        or ancestry_record.get("argv")
        != ["git", "-C", str(Path(root)), "rev-list", "HEAD"]
        or ancestry_record.get("exit_code") != 0
        or ancestry_record.get("stdout_sha256")
        != hashlib.sha256(ancestry_stdout).hexdigest()
        or ancestry_record.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
        or ancestry_record.get("evidence_request") is not False
        or ancestry_record.get("runner_state") != "active"
    ):
        raise GateError("push_journal_batch3_ancestry")
    expected_preflight = _push_preflight_digest(
        handoff=handoff, handoff_raw=handoff_raw,
        handoff_commit=str(handoff_commit),
        preflight_state=preflight_state,
    )
    if preflight_sha256 != expected_preflight:
        raise GateError("push_journal_terminal")
    _verify_push_handoff_tail(
        root=Path(root), records=records, handoff=handoff,
        handoff_raw=handoff_raw, handoff_commit=str(handoff_commit),
        tail_end=len(records) - 3,
    )
    _verify_direct_handoff_git(
        root=Path(root), handoff=handoff, handoff_raw=handoff_raw,
        handoff_commit=str(handoff_commit),
    )
    return 0


def verify_staged_payload(
    *, root: Path, head: str, staged_paths: Sequence[str], manifest: dict[str, Any]
) -> None:
    if head != manifest.get("pre_network_seal_commit") or not FULL_SHA.fullmatch(head):
        raise GateError("staged_payload_head")
    hashes = manifest.get("candidate_file_sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise GateError("staged_payload_manifest")
    if not all(
        isinstance(path, str)
        and path
        and not path.startswith("/")
        and ".." not in Path(path).parts
        and FULL_SHA256.fullmatch(str(digest))
        for path, digest in hashes.items()
    ):
        raise GateError("staged_payload_manifest")
    expected = {PAYLOAD_PREFIX + path for path in hashes}
    expected.add(PAYLOAD_PREFIX + PAYLOAD_MANIFEST)
    if set(staged_paths) != expected or len(staged_paths) != len(expected):
        raise GateError("staged_payload_paths")
    for relative, expected_sha in hashes.items():
        path = Path(root) / PAYLOAD_PREFIX / relative
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha:
            raise GateError(f"staged_payload_hash: {relative}")


def verify_staged_worktree_state(
    *, staged_paths: Sequence[str], unstaged_paths: Sequence[str], status_lines: Sequence[str]
) -> None:
    if list(unstaged_paths):
        raise GateError("staged_payload_unstaged_drift")
    expected_status = {f"A  {path}" for path in staged_paths}
    if set(status_lines) != expected_status or len(status_lines) != len(expected_status):
        raise GateError("staged_payload_worktree_state")


def handle_verify_staged_payload(*, root: Path, authority: str, journal: Path) -> int:
    if not FULL_SHA.fullmatch(authority):
        raise GateError("authority_sha")
    try:
        manifest = json.loads(_manifest_path(Path(root)).read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"payload_manifest: {exc}") from exc
    if not Path(journal).is_file() or Path(journal).is_symlink():
        raise GateError("journal_missing")
    try:
        _admission.verify_payload_manifest_exact(
            root=Path(root),
            payload_root=_manifest_path(Path(root)).parent,
            authority=authority,
            journal=Path(journal),
        )
    except Exception as exc:
        raise GateError(f"payload_manifest_binding: {exc}") from exc
    runner = _common.TerminalCommandRunner(Path(journal))
    head_raw, _ = runner.run(["git", "-C", str(Path(root)), "rev-parse", "HEAD"])
    staged_raw, _ = runner.run(["git", "-C", str(Path(root)), "diff", "--cached", "--name-only"])
    unstaged_raw, _ = runner.run(["git", "-C", str(Path(root)), "diff", "--name-only"])
    status_raw, _ = runner.run([
        "git", "-C", str(Path(root)), "status", "--porcelain=v1", "--untracked-files=all"
    ])
    head = head_raw.decode("ascii", errors="strict").strip()
    staged = [line for line in staged_raw.decode("utf-8").splitlines() if line]
    verify_staged_payload(root=Path(root), head=head, staged_paths=staged, manifest=manifest)
    verify_staged_worktree_state(
        staged_paths=staged,
        unstaged_paths=[line for line in unstaged_raw.decode("utf-8").splitlines() if line],
        status_lines=[line for line in status_raw.decode("utf-8").splitlines() if line],
    )
    for path in staged:
        staged_bytes, _ = runner.run(["git", "-C", str(Path(root)), "show", f":{path}"])
        if staged_bytes != (Path(root) / path).read_bytes():
            raise GateError(f"staged_payload_index_drift: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    staged = commands.add_parser("verify-staged-payload")
    staged.add_argument("--root", type=Path, required=True)
    staged.add_argument("--authority", required=True)
    staged.add_argument("--journal", type=Path, required=True)
    build = commands.add_parser("build-handoff")
    build.add_argument("--root", type=Path, required=True)
    build.add_argument("--authority", required=True)
    build.add_argument("--journal", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify-handoff")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--handoff", type=Path, required=True)
    verify.add_argument("--authority", required=True)
    verify.add_argument("--journal", type=Path, required=True)
    push_once = commands.add_parser("push-once")
    push_once.add_argument("--root", type=Path, required=True)
    push_once.add_argument("--journal", type=Path, required=True)
    push_once.add_argument("--handoff", type=Path, required=True)
    push_once.add_argument("--handoff-commit", required=True)
    push = commands.add_parser("verify-push-journal")
    push.add_argument("--root", type=Path, required=True)
    push.add_argument("--journal", type=Path, required=True)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    handlers: dict[str, Callable[..., int]] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    active = handlers or {
        "verify-staged-payload": handle_verify_staged_payload,
        "build-handoff": handle_build_handoff,
        "verify-handoff": handle_verify_handoff,
        "push-once": handle_push_once,
        "verify-push-journal": handle_verify_push_journal,
    }
    values = vars(args).copy()
    command = values.pop("command")
    try:
        return int(active[command](**values))
    except Exception as exc:
        if (
            handlers is None
            and command != "verify-push-journal"
            and isinstance(values.get("journal"), Path)
            and values["journal"].is_file()
        ):
            _common.persist_cli_failure(values["journal"], f"handoff_{command}", exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
