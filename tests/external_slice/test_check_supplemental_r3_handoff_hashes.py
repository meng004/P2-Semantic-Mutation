from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(os.environ.get("SUPPLEMENTAL_R3_MODULE_ROOT", Path(__file__).resolve().parents[2]))


def load_checker(name: str = "check_supplemental_r3_handoff_hashes"):
    path = ROOT / "scripts/external_slice/check_supplemental_r3_handoff_hashes.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_direct_child_history_requires_exact_parent_and_single_path() -> None:
    checker = load_checker()
    checker.verify_direct_child_history(
        payload_commit="a" * 40,
        handoff_commit="b" * 40,
        handoff_parents=["a" * 40],
        changed_paths=["data/external_slice/supplemental_r3/HANDOFF_SUPPLEMENTAL_R3.json"],
    )
    with pytest.raises(checker.GateError, match="handoff_history"):
        checker.verify_direct_child_history(
            payload_commit="a" * 40,
            handoff_commit="b" * 40,
            handoff_parents=["c" * 40],
            changed_paths=["data/external_slice/supplemental_r3/HANDOFF_SUPPLEMENTAL_R3.json"],
        )


def test_handoff_requires_four_plan_hashes_and_bundle_binding() -> None:
    checker = load_checker("check_supplemental_r3_handoff_bind")
    handoff = {
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "amendment_id": "AMENDMENT_01_REF_ISOLATION",
        "bootstrap_addendum_id": "BOOTSTRAP_EXECUTION_ADDENDUM_03",
        "authority": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        "plan_sha256": ["1" * 64, "2" * 64, "3" * 64, "4" * 64],
        "bundle_commit": "a" * 40,
        "bundle_tree": "b" * 40,
        "bundle_manifest_sha256": "c" * 64,
        "design_sha256": "9" * 64,
        "spool_sha256": "d" * 64,
        "vm_green_report_sha256": "8" * 64,
        "vm_green": {
            "node_count": 69,
            "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
            "evidence_request_count": 0,
        },
        "environment_seal_commit_command": [
            "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
        ],
        "pre_network_seal_commit": "f" * 40,
        "pre_network_seal_sha256": "0" * 64,
        "pre_network_journal_prefix_sha256": "5" * 64,
        "pre_network_journal_record_count": 19,
        "journal_sha256": "6" * 64,
        "journal_record_count": 40,
        "pre_network_evidence_request_count": 0,
        "evidence_request_count": 19,
        "payload_commit": "e" * 40,
        "quota_results": {"cornellius-gp/gpytorch": 2, "jonathf/chaospy": 3, "SALib/SALib": 3},
        "verdict": "SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT",
        "research_evidence_boundary": {
            "candidate_evidence_only": True,
            "manuscript_claims_unmodified": True,
            "requires_separate_local_desktop_evidence_audit_pass": True,
        },
        "terminal_commands": [
            list(checker.PAYLOAD_COMMIT_COMMAND),
            list(checker.HANDOFF_COMMIT_COMMAND),
            list(checker.PUSH_COMMAND),
        ],
    }
    checker.verify_handoff_bindings(handoff)
    handoff["plan_sha256"] = handoff["plan_sha256"][:3]
    with pytest.raises(checker.GateError, match="plan_lineage"):
        checker.verify_handoff_bindings(handoff)


def test_terminal_commands_allow_one_push_and_no_pr_or_merge(
    tmp_path: Path, monkeypatch,
) -> None:
    checker = load_checker("check_supplemental_r3_terminal")
    commands = [
        list(checker.PAYLOAD_COMMIT_COMMAND),
        list(checker.HANDOFF_COMMIT_COMMAND),
        list(checker.PUSH_COMMAND),
    ]
    checker.verify_terminal_commands(commands)
    with pytest.raises(checker.GateError, match="terminal_commands"):
        checker.verify_terminal_commands(commands + [["gh", "pr", "create"]])
    with pytest.raises(checker.GateError, match="terminal_commands"):
        checker.verify_terminal_commands([
            list(checker.PAYLOAD_COMMIT_COMMAND), list(checker.HANDOFF_COMMIT_COMMAND),
            ["git", "push", "--force", "origin", "cursor/evidence"],
        ])
    mutated = [list(command) for command in commands]
    mutated[0][-1] = "different payload message"
    with pytest.raises(checker.GateError, match="terminal_commands"):
        checker.verify_terminal_commands(mutated)
    root = tmp_path / "root"
    handoff_path = root / checker.HANDOFF_PATH
    handoff_path.parent.mkdir(parents=True)
    payload_commit = "b" * 40
    handoff_commit = "c" * 40
    handoff = {
        "payload_commit": payload_commit,
        "pre_network_journal_prefix_sha256": "1" * 64,
        "pre_network_journal_record_count": 1,
        "journal_sha256": "2" * 64,
        "journal_record_count": 2,
    }
    handoff_raw = checker._common.canonical_json_bytes(handoff) + b"\n"
    handoff_path.write_bytes(handoff_raw)
    root_text = str(root)
    command_outputs = [
        (["git", "-C", root_text, "rev-parse", "HEAD"], (handoff_commit + "\n").encode()),
        (["git", "-C", root_text, "rev-list", "--parents", "-n", "1", handoff_commit], (handoff_commit + " " + payload_commit + "\n").encode()),
        (["git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", handoff_commit], (checker.HANDOFF_PATH + "\n").encode()),
        (["git", "-C", root_text, "show", f"HEAD:{checker.HANDOFF_PATH}"], handoff_raw),
        (["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"], b""),
    ]
    push_journal = tmp_path / "push.jsonl"
    prefix = []
    for sequence, (argv, stdout) in enumerate(command_outputs, 1):
        prefix.append({
            "sequence": sequence,
            "stage": "command",
            "argv": argv,
            "exit_code": 0,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            "evidence_request": False,
            "evidence_request_count": 0,
            "runner_state": "active",
        })
    prefix_bytes = b"".join(
        checker._common.canonical_json_bytes(record) + b"\n" for record in prefix
    )
    push_journal.write_bytes(prefix_bytes)
    runner = checker._common.TerminalCommandRunner(
        push_journal, executor=lambda argv: (0, b"pushed", b"")
    )
    preflight_sha256 = checker._push_preflight_digest(
        handoff=handoff, handoff_raw=handoff_raw,
        handoff_commit=handoff_commit,
        preflight_state={
            "preflight_command_record_start": 1,
            "preflight_command_record_end": 5,
            "preflight_command_record_count": 5,
            "preflight_command_sha256": hashlib.sha256(prefix_bytes).hexdigest(),
            "pre_push_journal_record_count": 5,
            "pre_push_journal_sha256": hashlib.sha256(prefix_bytes).hexdigest(),
        },
    )
    runner.run(
        list(checker.PUSH_COMMAND), push_handoff_commit=handoff_commit,
        push_preflight_sha256=preflight_sha256,
    )
    with pytest.raises(checker.GateError):
        checker.handle_verify_push_journal(root=root, journal=push_journal)
    monkeypatch.setattr(
        checker, "_load_push_static_lineage",
        lambda **kwargs: (handoff, handoff_raw),
    )
    monkeypatch.setattr(checker, "_verify_direct_handoff_git", lambda **kwargs: None)
    assert checker.handle_verify_push_journal(root=root, journal=push_journal) == 0

    forged = tmp_path / "forged-push.jsonl"
    forged.write_bytes(checker._common.canonical_json_bytes({
        "sequence": 1,
        "stage": "push_completion",
        "argv": list(checker.PUSH_COMMAND),
        "handoff_commit": handoff_commit,
        "preflight_sha256": preflight_sha256,
        "exit_code": 0,
        "evidence_request": False,
        "runner_state": "success_closed",
    }) + b"\n")
    with pytest.raises(checker.GateError, match="push_journal_terminal"):
        checker.handle_verify_push_journal(root=root, journal=forged)


def test_push_preflight_rejects_wrong_git_head_before_push_intent_or_executor(
    tmp_path: Path, monkeypatch,
) -> None:
    checker = load_checker("check_supplemental_r3_push_preflight")
    root = tmp_path / "root"
    handoff_path = root / checker.HANDOFF_PATH
    handoff_path.parent.mkdir(parents=True)
    handoff_raw = b"{}\n"
    handoff_path.write_bytes(handoff_raw)
    journal = tmp_path / "journal.jsonl"
    journal.write_bytes(checker._common.canonical_json_bytes({
        "sequence": 1, "stage": "command", "evidence_request": False,
        "runner_state": "active",
    }) + b"\n")
    handoff = {
        "payload_commit": "b" * 40,
        "pre_network_journal_prefix_sha256": "1" * 64,
        "pre_network_journal_record_count": 1,
        "journal_sha256": "2" * 64,
        "journal_record_count": 2,
    }
    monkeypatch.setattr(
        checker, "_load_push_static_lineage",
        lambda **kwargs: (handoff, handoff_raw),
    )
    monkeypatch.setattr(checker, "_verify_push_handoff_tail", lambda **kwargs: None)
    def reject_head(**kwargs):
        runner = checker._common.TerminalCommandRunner(journal)
        runner.fail_invariant("push_preflight", "head")
        raise checker.GateError("push_preflight: head")

    monkeypatch.setattr(checker, "_run_push_git_preflight", reject_head)
    with pytest.raises(checker.GateError, match="push_preflight"):
        checker.main([
            "push-once", "--root", str(root), "--journal", str(journal),
            "--handoff", str(handoff_path), "--handoff-commit", "c" * 40,
        ])
    records = [json.loads(line) for line in journal.read_text().splitlines()]
    assert not any(record.get("stage") == "push_intent" for record in records)
    assert any(record.get("stage") == "invariant_failure" for record in records)
    assert records[-1]["runner_state"] == "terminal"


def test_push_preflight_reads_real_git_head_parent_path_bytes_and_clean_state(
    tmp_path: Path,
) -> None:
    checker = load_checker("check_supplemental_r3_push_real_git")
    root = tmp_path / "repository"
    root.mkdir()

    def git(*args: str) -> bytes:
        return subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True,
            check=True,
        ).stdout

    git("init", "-q")
    git("config", "user.email", "audit@example.invalid")
    git("config", "user.name", "Audit")
    (root / "payload.txt").write_text("payload\n", encoding="utf-8")
    git("add", "payload.txt")
    git("commit", "-q", "-m", "payload")
    payload_commit = git("rev-parse", "HEAD").decode().strip()
    handoff = {"payload_commit": payload_commit}
    handoff_raw = checker._common.canonical_json_bytes(handoff) + b"\n"
    handoff_path = root / checker.HANDOFF_PATH
    handoff_path.parent.mkdir(parents=True)
    handoff_path.write_bytes(handoff_raw)
    git("add", checker.HANDOFF_PATH)
    git("commit", "-q", "-m", "handoff")
    handoff_commit = git("rev-parse", "HEAD").decode().strip()
    checker._verify_direct_handoff_git(
        root=root, handoff=handoff, handoff_raw=handoff_raw,
        handoff_commit=handoff_commit,
    )
    with pytest.raises(checker.GateError, match="push_git_handoff"):
        checker._verify_direct_handoff_git(
            root=root, handoff=handoff, handoff_raw=handoff_raw,
            handoff_commit=payload_commit,
        )
    preflight_journal = tmp_path / "preflight.jsonl"
    runner, state = checker._run_push_git_preflight(
        root=root, journal=preflight_journal, handoff=handoff,
        handoff_raw=handoff_raw, handoff_commit=handoff_commit,
    )
    assert runner.terminal is False
    assert state["preflight_command_record_count"] == 5
    assert state["preflight_command_record_start"] == 1
    assert state["preflight_command_record_end"] == 5
    records = [json.loads(line) for line in preflight_journal.read_text().splitlines()]
    assert [record["stage"] for record in records] == ["command"] * 5

    wrong_journal = tmp_path / "wrong-head.jsonl"
    with pytest.raises(checker.GateError, match="push_preflight: head"):
        checker._run_push_git_preflight(
            root=root, journal=wrong_journal, handoff=handoff,
            handoff_raw=handoff_raw, handoff_commit=payload_commit,
        )
    wrong_records = [json.loads(line) for line in wrong_journal.read_text().splitlines()]
    assert [record["stage"] for record in wrong_records] == [
        "command", "invariant_failure",
    ]
    assert wrong_records[-1]["runner_state"] == "terminal"


def test_handoff_cli_exposes_staged_build_and_verify_only() -> None:
    checker = load_checker("check_supplemental_r3_handoff_cli")
    parser = checker.build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {
        "verify-staged-payload", "build-handoff", "verify-handoff", "push-once",
        "verify-push-journal",
    }


def test_handoff_main_dispatches_selected_handler(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_handoff_main")
    calls = []
    handlers = {name: (lambda selected: lambda **kwargs: calls.append((selected, kwargs)) or 0)(name) for name in (
        "verify-staged-payload", "build-handoff", "verify-handoff"
    )}
    assert checker.main([
        "verify-handoff", "--handoff", str(tmp_path / "handoff.json"),
        "--root", str(tmp_path / "root"), "--authority", "a" * 40, "--journal", str(tmp_path / "journal.jsonl"),
    ], handlers=handlers) == 0
    assert calls[0][0] == "verify-handoff"


def test_default_build_and_verify_handoff_roundtrip(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_handoff_roundtrip")
    root = tmp_path / "root"
    root.mkdir()
    journal = tmp_path / "journal"
    initial_record = {
        "sequence": 1,
        "stage": "journal_initialized",
        "exit_code": 0,
        "evidence_request": False,
        "runner_state": "active",
    }
    journal.write_bytes(checker._common.canonical_json_bytes(initial_record) + b"\n")
    prefix_sha = hashlib.sha256(journal.read_bytes()).hexdigest()
    bundle_path = root / checker.BUNDLE_MANIFEST_PATH
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "authority": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        "design_sha256": "9" * 64,
        "parent_plan_sha256": ["1" * 64, "2" * 64, "3" * 64],
    }
    bundle_path.write_text(json.dumps(bundle) + "\n", encoding="utf-8")
    seal_path = root / checker.VM_SEAL_PATH
    seal = {
        "authority": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        "design_sha256": "9" * 64,
        "plan_sha256": ["1" * 64, "2" * 64, "3" * 64, "4" * 64],
        "bundle_commit": "a" * 40,
        "bundle_tree": "b" * 40,
        "bundle_manifest_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
        "spool_sha256": "d" * 64,
        "vm_green_report_sha256": "8" * 64,
        "vm_green": {
            "node_count": 69,
            "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
            "evidence_request_count": 0,
        },
        "environment_seal_commit_command": [
            "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
        ],
    }
    seal_path.write_text(json.dumps(seal) + "\n", encoding="utf-8")
    payload = {
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "authority": "31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        "bundle_commit": "a" * 40,
        "bundle_tree": "b" * 40,
        "bundle_manifest_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
        "design_sha256": "9" * 64,
        "spool_sha256": "d" * 64,
        "vm_green_report_sha256": "8" * 64,
        "vm_green": {
            "node_count": 69,
            "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
            "evidence_request_count": 0,
        },
        "environment_seal_commit_command": [
            "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
        ],
        "pre_network_seal_commit": "e" * 40,
        "pre_network_seal_sha256": hashlib.sha256(seal_path.read_bytes()).hexdigest(),
        "pre_network_journal_prefix_sha256": prefix_sha,
        "pre_network_journal_record_count": 1,
        "journal_sha256": prefix_sha,
        "journal_record_count": 1,
        "pre_network_evidence_request_count": 0,
        "evidence_request_count": 1,
        "candidate_file_sha256": {"ISSUE_SNAPSHOT.json": "9" * 64},
        "plan_sha256": ["1" * 64, "2" * 64, "3" * 64, "4" * 64],
        "quota_results": checker.EXPECTED_QUOTAS,
        "verdict": "SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT",
        "research_evidence_boundary": {
            "candidate_evidence_only": True,
            "manuscript_claims_unmodified": True,
            "requires_separate_local_desktop_evidence_audit_pass": True,
        },
        "terminal_commands": [
            list(checker.PAYLOAD_COMMIT_COMMAND),
            list(checker.HANDOFF_COMMIT_COMMAND),
            list(checker.PUSH_COMMAND),
        ],
    }
    manifest_path = root / checker.PAYLOAD_PREFIX / checker.PAYLOAD_MANIFEST
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    checker._admission.verify_payload_manifest_exact = lambda **kwargs: payload
    checker._read_payload_commit = lambda **kwargs: "f" * 40
    checker._verify_handoff_git_history = lambda **kwargs: None
    output = root / checker.HANDOFF_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    assert checker.handle_build_handoff(root=root, authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4", journal=journal, output=output) == 0
    assert checker.handle_verify_handoff(root=root, handoff=output, authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4", journal=journal) == 0


def test_verify_staged_payload_uses_manifest_exact_allowlist(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_staged_payload")
    manifest = {
        "bundle_commit": "a" * 40,
        "pre_network_seal_commit": "e" * 40,
        "candidate_file_sha256": {},
    }
    prefix = "data/external_slice/supplemental_r3/"
    staged = [
        prefix + "ISSUE_SNAPSHOT.json",
        prefix + "REVIEW_QUEUE.json",
        prefix + checker.PAYLOAD_MANIFEST,
    ]
    for relative, raw in (("ISSUE_SNAPSHOT.json", b"issue\n"), ("REVIEW_QUEUE.json", b"queue\n")):
        path = tmp_path / prefix / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        manifest["candidate_file_sha256"][relative] = hashlib.sha256(raw).hexdigest()
    checker.verify_staged_payload(root=tmp_path, head="e" * 40, staged_paths=staged, manifest=manifest)
    with pytest.raises(checker.GateError, match="staged_payload"):
        checker.verify_staged_payload(
            root=tmp_path,
            head="e" * 40,
            staged_paths=staged + ["data/external_slice/supplemental_r2/SCOPE.json"],
            manifest=manifest,
        )


def test_staged_payload_rejects_unstaged_or_untracked_drift() -> None:
    checker = load_checker("check_supplemental_r3_staged_drift")
    staged = [checker.PAYLOAD_PREFIX + "ISSUE_SNAPSHOT.json"]
    checker.verify_staged_worktree_state(
        staged_paths=staged,
        unstaged_paths=[],
        status_lines=[f"A  {staged[0]}"],
    )
    with pytest.raises(checker.GateError, match="unstaged_drift"):
        checker.verify_staged_worktree_state(
            staged_paths=staged,
            unstaged_paths=[checker.VM_SEAL_PATH],
            status_lines=[f"A  {staged[0]}", f" M {checker.VM_SEAL_PATH}"],
        )
    with pytest.raises(checker.GateError, match="worktree_state"):
        checker.verify_staged_worktree_state(
            staged_paths=staged,
            unstaged_paths=[],
            status_lines=[f"A  {staged[0]}", "?? unexpected.json"],
        )
