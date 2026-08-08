from __future__ import annotations

import importlib.util
import csv
import hashlib
import json
import os
from pathlib import Path

import pytest


ROOT = Path(os.environ.get("SUPPLEMENTAL_R3_MODULE_ROOT", Path(__file__).resolve().parents[2]))


def load_checker(name: str = "check_supplemental_r3_admission"):
    path = ROOT / "scripts/external_slice/check_supplemental_r3_admission.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_decision_biconditional_and_blind_fields() -> None:
    checker = load_checker()
    row = {
        "crit_real_public_fix": "PASS",
        "crit_in_numerical_scope": "PASS",
        "crit_dual_arm_repro": "PENDING",
        "decision": "ADMIT_PENDING_REPRO",
        "analysis_id": "",
        "alias": "",
    }
    checker.validate_decision(row)
    row["crit_real_public_fix"] = "FAIL"
    with pytest.raises(checker.GateError, match="decision_biconditional"):
        checker.validate_decision(row)


def test_quota_vector_is_exact_and_independent() -> None:
    checker = load_checker("check_supplemental_r3_quota")
    checker.verify_quota_results({"cornellius-gp/gpytorch": 2, "jonathf/chaospy": 3, "SALib/SALib": 3})
    with pytest.raises(checker.GateError, match="quota_vector"):
        checker.verify_quota_results({"cornellius-gp/gpytorch": 3, "jonathf/chaospy": 2, "SALib/SALib": 3})


def test_independent_replay_rejects_partial_errors_and_repeated_cursors() -> None:
    checker = load_checker("check_supplemental_r3_raw_replay_fail_closed")
    for label in ("discovery", "issue"):
        with pytest.raises(checker.GateError, match=f"{label}_graphql_errors"):
            checker._reject_replay_graphql_errors(
                {"data": {"repository": {}}, "errors": [{"message": "partial"}]},
                label,
            )
    for label in ("discovery", "issue_comment", "issue_timeline"):
        seen: set[str] = set()
        page_info = {"hasNextPage": True, "endCursor": "repeat"}
        assert checker._replay_next_cursor(page_info, seen, label) == "repeat"
        with pytest.raises(checker.GateError, match=f"{label}_cursor_repeat"):
            checker._replay_next_cursor(page_info, seen, label)


def test_five_layer_binding_rejects_one_field_mutation() -> None:
    checker = load_checker("check_supplemental_r3_binding")
    chain = {
        "snapshot": {"record_id": "s1", "sha256": "a" * 64},
        "queue": {"snapshot_record_id": "s1", "snapshot_record_sha256": "a" * 64},
        "decision": {"snapshot_record_id": "s1", "snapshot_record_sha256": "a" * 64},
        "sheet": {"snapshot_record_id": "s1", "snapshot_record_sha256": "a" * 64},
        "evidence": {"snapshot_record_id": "s1", "snapshot_record_sha256": "a" * 64},
    }
    checker.verify_five_layer_binding(chain)
    chain["evidence"]["snapshot_record_sha256"] = "b" * 64
    with pytest.raises(checker.GateError, match="five_layer_binding"):
        checker.verify_five_layer_binding(chain)


def test_candidate_sheet_requires_exact_complete_header(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_sheet_header")
    decision = {key: "" for key in checker.CANDIDATE_SHEET_FIELDS}
    truncated = tmp_path / "candidate.csv"
    with truncated.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=checker.CANDIDATE_SHEET_FIELDS[:-1])
        writer.writeheader()
        writer.writerow({key: decision[key] for key in checker.CANDIDATE_SHEET_FIELDS[:-1]})
    with pytest.raises(checker.GateError, match="sheet_header"):
        checker.verify_sheet_projection(truncated, [decision])


def test_transactional_publication_exposes_only_complete_old_or_new_directory(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_publish")
    candidate = tmp_path / "candidate-payload"
    target = tmp_path / "published-payload"
    candidate.mkdir()
    target.mkdir()
    (target / "frozen.json").write_text("frozen", encoding="utf-8")
    (candidate / "one.json").write_text("one", encoding="utf-8")
    (candidate / "two.json").write_text("two", encoding="utf-8")
    with pytest.raises(checker.GateError, match="publication_failed"):
        checker.publish_payload_directory_atomically(
            candidate, target, fail_before_exchange=True
        )
    assert sorted(path.name for path in candidate.iterdir()) == ["one.json", "two.json"]
    assert [path.name for path in target.iterdir()] == ["frozen.json"]

    exchanges = []

    def exchange(left: Path, right: Path) -> None:
        exchanges.append((left, right))
        temporary = tmp_path / "synthetic-exchange"
        left.rename(temporary)
        right.rename(left)
        temporary.rename(right)

    checker.publish_payload_directory_atomically(candidate, target, exchange=exchange)
    assert len(exchanges) == 1
    assert {path.name for path in target.iterdir()} == {"frozen.json", "one.json", "two.json"}
    assert not exchanges[0][1].exists()


def test_publish_rejects_wrong_branch_before_operation_intent(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_publish_branch")
    journal = tmp_path / "journal.jsonl"
    with pytest.raises(checker.GateError, match="evidence_branch"):
        checker.handle_publish_payload(
            root=tmp_path / "root",
            candidate_root=tmp_path / "candidate",
            authority="a" * 40,
            journal=journal,
            branch="wrong-branch",
        )
    assert not journal.exists()


def test_independent_stop_closure_rejects_post_stop_and_r2_fix_reuse() -> None:
    checker = load_checker("check_supplemental_r3_stop_closure")
    queue = [
        {"neutral_id": "A01", "repository": "r/a", "collision": False, "status": "REVIEWED"},
        {"neutral_id": "A02", "repository": "r/a", "collision": False, "status": "NOT_REVIEWED_AFTER_STOP"},
        {"neutral_id": "", "repository": "r/a", "collision": True, "status": "COLLISION"},
    ]
    decision = {
        "neutral_id": "A01", "repository": "r/a", "decision": "ADMIT_PENDING_REPRO",
        "fixed_sha": "a" * 40,
    }
    checker.verify_review_stop_closure(
        queue, [decision], {"r/a": 1}, known_fix_shas=set()
    )
    with pytest.raises(checker.GateError, match="decision_after_stop"):
        checker.verify_review_stop_closure(
            queue,
            [decision, {**decision, "neutral_id": "A02", "fixed_sha": "b" * 40}],
            {"r/a": 1},
            known_fix_shas=set(),
        )
    with pytest.raises(checker.GateError, match="known_fix_reuse"):
        checker.verify_review_stop_closure(
            queue, [decision], {"r/a": 1}, known_fix_shas={"a" * 40}
        )


def test_payload_manifest_projection_is_exact_and_rejects_extra_fields() -> None:
    checker = load_checker("check_supplemental_r3_manifest_projection")
    expected = {"protocol": "p", "authority": "a"}
    checker.verify_exact_manifest_projection(expected, expected)
    with pytest.raises(checker.GateError, match="payload_manifest_binding"):
        checker.verify_exact_manifest_projection({**expected, "readiness": True}, expected)


def test_vm_seal_must_equal_bytes_committed_by_seal_commit(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_committed_seal")
    root = tmp_path / "root"
    seal_path = root / checker.VM_SEAL_REL
    seal_path.parent.mkdir(parents=True)
    seal_path.write_bytes(b"current-seal\n")
    seal_commit = "e" * 40
    bundle_commit = "a" * 40

    class Runner:
        def __init__(self, path):
            del path

        def run(self, argv):
            if "rev-list" in argv:
                return f"{seal_commit} {bundle_commit}\n".encode(), b""
            if "diff-tree" in argv:
                return (checker.VM_SEAL_REL.as_posix() + "\n").encode(), b""
            if "show" in argv:
                return b"different-committed-seal\n", b""
            raise AssertionError(argv)

    checker._common.TerminalCommandRunner = Runner
    with pytest.raises(checker.GateError, match="committed_bytes"):
        checker._read_vm_seal_commit(
            root=root,
            journal=tmp_path / "journal",
            seal={"bundle_commit": bundle_commit},
            expected_commit=seal_commit,
        )


def test_journal_boundaries_bind_materialize_and_candidate_collection(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_journal_boundaries")

    def write_records(path: Path, records: list[dict]) -> None:
        path.write_bytes(b"".join(
            checker._common.canonical_json_bytes(record) + b"\n" for record in records
        ))

    seal_journal = tmp_path / "seal-journal.jsonl"
    seal_records = [
        {
            "sequence": 1,
            "stage": "operation_intent",
            "operation_name": "materialize_pre_network_seal",
            "operation_key": "1:materialize_pre_network_seal",
            "evidence_request": False,
            "runner_state": "pending",
        },
        {
            "sequence": 2,
            "stage": "operation",
            "operation_key": "1:materialize_pre_network_seal",
            "metadata": {"sha256": "a" * 64},
            "evidence_request": False,
            "runner_state": "active",
        },
    ]
    write_records(seal_journal, seal_records)
    checker._verify_pre_network_seal_operation_completion(
        journal=seal_journal,
        seal={"journal_record_count": 1},
        seal_sha256="a" * 64,
    )
    seal_records[1]["metadata"]["sha256"] = "b" * 64
    write_records(seal_journal, seal_records)
    with pytest.raises(checker.GateError, match="pre_network_operation_boundary"):
        checker._verify_pre_network_seal_operation_completion(
            journal=seal_journal,
            seal={"journal_record_count": 1},
            seal_sha256="a" * 64,
        )

    acquisition_journal = tmp_path / "acquisition-journal.jsonl"
    seal_commit = "c" * 40
    seal_sha256 = "d" * 64
    ancestry_stdout = (("1" * 40) + "\n" + ("2" * 40) + "\n").encode()
    batch3_ancestry = {
        "count": 2,
        "sha256": hashlib.sha256(ancestry_stdout).hexdigest(),
    }
    root_text = "/tmp/repository"
    acquisition_records = [
        {
            "sequence": 1, "stage": "operation_intent",
            "operation_name": "verify_environment_seal",
            "operation_key": "1:verify_environment_seal",
            "evidence_request": False, "runner_state": "pending",
        },
        {
            "sequence": 2, "stage": "operation", "operation_key": "1:verify_environment_seal",
            "metadata": {
                "seal_commit": seal_commit,
                "seal_sha256": seal_sha256,
                "batch3_ancestry": batch3_ancestry,
            },
            "evidence_request": False, "runner_state": "active",
        },
        {
            "sequence": 3, "stage": "command",
            "argv": ["git", "-C", root_text, "rev-parse", "HEAD"],
            "stdout_sha256": hashlib.sha256((seal_commit + "\n").encode()).hexdigest(),
            "exit_code": 0, "evidence_request": False, "runner_state": "active",
        },
        {
            "sequence": 4, "stage": "command",
            "argv": ["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"],
            "stdout_sha256": hashlib.sha256(b"").hexdigest(),
            "exit_code": 0, "evidence_request": False, "runner_state": "active",
        },
        {
            "sequence": 5, "stage": "operation_intent",
            "operation_name": "candidate_collection", "operation_key": "6:candidate_collection",
            "metadata": {
                "environment_seal_commit": seal_commit,
                "environment_seal_sha256": seal_sha256,
                "batch3_ancestry": batch3_ancestry,
            },
            "evidence_request": False, "runner_state": "pending",
        },
        {
            "sequence": 6, "stage": "command", "request_key": "issue-page-1",
            "evidence_request": True, "runner_state": "active",
        },
        {
            "sequence": 7, "stage": "operation", "operation_key": "6:candidate_collection",
            "evidence_request": False, "runner_state": "active",
        },
        {
            "sequence": 8, "stage": "operation_intent", "operation_name": "build_payload_manifest",
            "operation_key": "8:build_payload_manifest", "evidence_request": False,
            "runner_state": "pending",
        },
    ]
    acquisition_records.insert(4, {
        "sequence": 5, "stage": "command",
        "argv": ["git", "-C", root_text, "rev-list", "HEAD"],
        "stdout_sha256": batch3_ancestry["sha256"],
        "exit_code": 0, "evidence_request": False, "runner_state": "active",
    })
    for sequence, record in enumerate(acquisition_records, 1):
        record["sequence"] = sequence
    write_records(acquisition_journal, acquisition_records)
    state = checker._candidate_collection_prefix_state(acquisition_journal)
    assert state["journal_record_count"] == 8
    assert state["evidence_request_count"] == 1
    acquisition_records.append({
        "sequence": 10, "stage": "command", "request_key": "late-page",
        "evidence_request": True, "runner_state": "active",
    })
    write_records(acquisition_journal, acquisition_records)
    with pytest.raises(checker.GateError, match="evidence_request_after_collection"):
        checker._candidate_collection_prefix_state(acquisition_journal)


def test_candidate_payload_requires_exact_artifact_path_set() -> None:
    checker = load_checker("check_supplemental_r3_paths")
    expected = {
        "ISSUE_SNAPSHOT.json",
        "REVIEW_QUEUE.json",
        "REVIEW_DECISIONS.json",
        "admission_sheet.cursor_candidate.csv",
        "EVIDENCE_SNAPSHOT.json",
    }
    checker.verify_candidate_path_set(expected, expected)
    with pytest.raises(checker.GateError, match="candidate_path_set"):
        checker.verify_candidate_path_set(expected | {"readiness.json"}, expected)


def test_environment_journal_provenance_rejects_omitted_trace_command(
    tmp_path: Path, monkeypatch,
) -> None:
    checker = load_checker("check_supplemental_r3_environment_provenance")
    root = tmp_path / "repository"
    root.mkdir()
    journal = tmp_path / "journal.jsonl"
    authority = "a" * 40
    bundle_commit = "d" * 40
    seal_commit = "e" * 40
    seal_sha256 = "f" * 64
    ancestry_stdout = (("1" * 40) + "\n" + ("2" * 40) + "\n").encode()
    batch3_ancestry = {
        "count": 2,
        "sha256": hashlib.sha256(ancestry_stdout).hexdigest(),
    }
    seal = {
        "authority": authority,
        "bundle_commit": bundle_commit,
        "bundle_tree": "1" * 40,
        "bundle_manifest_sha256": "2" * 64,
        "design_sha256": "3" * 64,
        "plan_sha256": ["4" * 64, "5" * 64, "6" * 64, "7" * 64],
        "vm_green_report_sha256": "8" * 64,
        "journal_record_count": 1,
        "frozen_inputs": {
            "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d",
            "r2_path_count": 634,
            "admission_blob": "5ef073d4d6297639695491c46d20733236bede52",
            "batch3_deny_consistent": True,
        },
    }
    bundle = {"authority": authority, "commits": {}}
    trace_argv = ["git", "-C", str(root), "rev-parse", "TRACE"]
    monkeypatch.setattr(
        checker,
        "_expected_environment_command_trace",
        lambda **kwargs: [(trace_argv, b"trace\n")],
        raising=False,
    )

    def command(sequence, argv, stdout=b""):
        return {
            "sequence": sequence, "stage": "command", "argv": argv,
            "exit_code": 0, "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            "evidence_request": False, "evidence_request_count": 0,
            "runner_state": "active",
        }

    def write_journal(active_records):
        journal.write_bytes(b"".join(
            checker._common.canonical_json_bytes(record) + b"\n"
            for record in active_records
        ))

    records = [{
        "sequence": 1, "stage": "operation_intent",
        "operation_name": "materialize_pre_network_seal",
        "operation_key": "1:materialize_pre_network_seal",
        "evidence_request": False, "runner_state": "pending",
    }]
    seal["journal_prefix_sha256"] = hashlib.sha256(
        checker._common.canonical_json_bytes(records[0]) + b"\n"
    ).hexdigest()
    records.extend([
        {
            "sequence": 2, "stage": "operation",
            "operation_key": "1:materialize_pre_network_seal",
            "metadata": {"sha256": seal_sha256},
            "evidence_request": False, "runner_state": "active",
        },
        command(3, ["git", "add", checker.VM_SEAL_REL.as_posix()]),
        command(4, list(checker.ENVIRONMENT_SEAL_COMMIT_COMMAND)),
        command(5, trace_argv, b"trace\n"),
        {
            "sequence": 6, "stage": "operation_intent",
            "operation_name": "verify_environment_seal",
            "operation_key": "6:verify_environment_seal",
            "metadata": {"seal_commit": seal_commit, "seal_sha256": seal_sha256},
            "evidence_request": False, "runner_state": "pending",
        },
        {
            "sequence": 7, "stage": "operation",
            "operation_key": "6:verify_environment_seal",
            "metadata": {
                "seal_commit": seal_commit, "seal_sha256": seal_sha256,
                "vm_green_report_sha256": seal["vm_green_report_sha256"],
                "frozen_inputs": seal["frozen_inputs"],
                "batch3_ancestry": batch3_ancestry,
                "evidence_request_count": 0,
            },
            "evidence_request": False, "runner_state": "active",
        },
        command(8, ["git", "-C", str(root), "rev-parse", "HEAD"], (seal_commit + "\n").encode()),
        command(9, ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"]),
        command(
            10,
            ["git", "-C", str(root), "rev-list", "HEAD"],
            ancestry_stdout,
        ),
        {
            "sequence": 11, "stage": "operation_intent",
            "operation_name": "candidate_collection",
            "operation_key": "11:candidate_collection",
            "metadata": {
                "candidate_root": str(tmp_path / "candidate"), "authority": authority,
                "environment_seal_commit": seal_commit,
                "environment_seal_sha256": seal_sha256,
                "batch3_ancestry": batch3_ancestry,
            },
            "evidence_request": False, "runner_state": "pending",
        },
    ])
    write_journal(records)
    checker._verify_environment_journal_provenance(
        root=root, journal=journal, seal=seal, bundle=bundle,
        seal_sha256=seal_sha256, seal_raw=b"sealed\n",
    )

    omitted = [record for record in records if record.get("argv") != trace_argv]
    for sequence, record in enumerate(omitted, 1):
        record["sequence"] = sequence
    write_journal(omitted)
    with pytest.raises(checker.GateError, match="environment_journal_provenance"):
        checker._verify_environment_journal_provenance(
            root=root, journal=journal, seal=seal, bundle=bundle,
            seal_sha256=seal_sha256, seal_raw=b"sealed\n",
        )


def test_environment_trace_binds_red_and_green_commit_trees_in_order(
    tmp_path: Path,
) -> None:
    checker = load_checker("check_supplemental_r3_environment_tree_trace")
    authority, red, green, bundle_commit, seal_commit = (
        character * 40 for character in "abcde"
    )
    red_tree, green_tree = "1" * 40, "2" * 40

    def entry(index: int) -> dict:
        return {
            "path": f"p{index}", "mode": "100644", "type": "blob",
            "oid": "3" * 40, "sha256": "4" * 64,
        }

    seal = {
        "authority": authority,
        "bundle_commit": bundle_commit,
        "bundle_tree": "5" * 40,
    }
    bundle = {
        "authority_tree": "6" * 40,
        "commits": {
            "red": {"commit": red, "parent": authority, "tree": red_tree},
            "green": {"commit": green, "parent": red, "tree": green_tree},
        },
        "frozen_inputs": {
            "r2_entries": [entry(index) for index in range(634)],
            "original_r3_entries": [entry(index) for index in range(12)],
            "admission_sheet": {"blob": "7" * 40, "sha256": "8" * 64},
        },
    }
    trace = checker._expected_environment_command_trace(
        root=tmp_path, seal=seal, bundle=bundle,
        seal_commit=seal_commit, seal_raw=b"seal\n",
        batch3_ancestry={"count": 438, "sha256": "9" * 64},
    )
    root_text = str(tmp_path)
    tree_rows = [
        (argv, stdout)
        for argv, stdout in trace
        if argv[:4] == ["git", "-C", root_text, "rev-parse"]
        and argv[-1] in {f"{red}^{{tree}}", f"{green}^{{tree}}"}
    ]
    assert tree_rows == [
        (["git", "-C", root_text, "rev-parse", f"{red}^{{tree}}"], (red_tree + "\n").encode()),
        (["git", "-C", root_text, "rev-parse", f"{green}^{{tree}}"], (green_tree + "\n").encode()),
    ]
    ancestry_rows = [
        (argv, stdout)
        for argv, stdout in trace
        if argv == ["git", "-C", root_text, "rev-list", "HEAD"]
    ]
    assert ancestry_rows == [
        (["git", "-C", root_text, "rev-list", "HEAD"], "9" * 64)
    ]
    bundle["commits"]["red"]["tree"] = "not-a-tree"
    with pytest.raises(checker.GateError, match="environment_journal_provenance"):
        checker._expected_environment_command_trace(
            root=tmp_path, seal=seal, bundle=bundle,
            seal_commit=seal_commit, seal_raw=b"seal\n",
            batch3_ancestry={"count": 438, "sha256": "9" * 64},
        )


def test_admission_cli_exposes_candidate_verify_and_publish_only() -> None:
    checker = load_checker("check_supplemental_r3_cli")
    parser = checker.build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {"build-payload", "verify-payload", "publish-payload"}


def test_admission_main_dispatches_selected_handler(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_main")
    calls = []
    handlers = {name: (lambda selected: lambda **kwargs: calls.append((selected, kwargs)) or 0)(name) for name in (
        "build-payload", "verify-payload", "publish-payload"
    )}
    assert checker.main([
        "verify-payload", "--root", str(tmp_path / "root"), "--candidate-root", str(tmp_path / "candidate"),
        "--authority", "a" * 40, "--journal", str(tmp_path / "journal.jsonl"), "--branch", "cursor/test-evidence",
    ], handlers=handlers) == 0
    assert calls[0][0] == "verify-payload"


def test_default_verify_payload_rejects_unbound_quota_only_forgery(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_default_verify")
    payload = tmp_path / "candidate/data/external_slice/supplemental_r3"
    payload.mkdir(parents=True)
    for name in ("ISSUE_SNAPSHOT.json", "REVIEW_QUEUE.json", "EVIDENCE_SNAPSHOT.json"):
        (payload / name).write_text("{}\n", encoding="utf-8")
    decisions = []
    for repo, count in checker.EXPECTED_QUOTAS.items():
        decisions.extend({"repository": repo, "decision": "ADMIT_PENDING_REPRO"} for _ in range(count))
    (payload / "REVIEW_DECISIONS.json").write_text(json.dumps({"rows": decisions}) + "\n", encoding="utf-8")
    (payload / "admission_sheet.cursor_candidate.csv").write_text("neutral_id\n", encoding="utf-8")
    with pytest.raises(checker.GateError, match="candidate_path_set"):
        checker.handle_verify_payload(
            root=tmp_path / "repo-root",
            candidate_root=tmp_path / "candidate",
            authority="a" * 40,
            journal=tmp_path / "journal.jsonl",
        )


def test_replay_rejects_duplicate_neutral_id_even_if_quota_counts_match(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_duplicate_decision")
    with pytest.raises(checker.GateError, match="decision_duplicate"):
        checker.verify_decision_uniqueness([
            {"neutral_id": "EXT-gpytorch-06", "repository": "cornellius-gp/gpytorch", "number": 1,
             "id": "I1", "url": "https://github.com/cornellius-gp/gpytorch/issues/1", "fixed_sha": "a" * 40},
            {"neutral_id": "EXT-gpytorch-06", "repository": "cornellius-gp/gpytorch", "number": 1,
             "id": "I1", "url": "https://github.com/cornellius-gp/gpytorch/issues/1", "fixed_sha": "a" * 40},
        ])


def test_excluded_decisions_allow_blank_fix_but_keep_issue_keys_unique() -> None:
    checker = load_checker("check_supplemental_r3_excluded_uniqueness")
    excluded = {
        "neutral_id": "EXT-gpytorch-06",
        "repository": "cornellius-gp/gpytorch",
        "number": 1,
        "id": "I1",
        "url": "https://github.com/cornellius-gp/gpytorch/issues/1",
        "fixed_sha": "",
        "decision": "EXCLUDED",
    }
    checker.verify_decision_uniqueness([excluded])
    duplicate_issue = dict(excluded, neutral_id="EXT-gpytorch-07")
    with pytest.raises(checker.GateError, match="decision_duplicate"):
        checker.verify_decision_uniqueness([excluded, duplicate_issue])


def test_replay_excluded_nonblank_fix_requires_exact_captured_record() -> None:
    checker = load_checker("check_supplemental_r3_excluded_fix_binding")
    captured_sha = "a" * 40
    captured_record = {"oid": captured_sha, "repository": "r/a"}
    used_fix_shas: set[str] = set()
    assert checker.bind_replayed_fix(
        fixed_sha=captured_sha,
        projected_fix_record=captured_record,
        unique_fix=captured_sha,
        valid_fix_records={captured_sha: captured_record},
        used_fix_shas=used_fix_shas,
    ) == captured_record
    assert used_fix_shas == {captured_sha}
    with pytest.raises(checker.GateError, match="ambiguous_or_missing_public_fix"):
        checker.bind_replayed_fix(
            fixed_sha="b" * 40,
            projected_fix_record=None,
            unique_fix=captured_sha,
            valid_fix_records={captured_sha: captured_record},
            used_fix_shas=set(),
        )
    with pytest.raises(checker.GateError, match="fix_collision"):
        checker.bind_replayed_fix(
            fixed_sha=captured_sha,
            projected_fix_record=captured_record,
            unique_fix=captured_sha,
            valid_fix_records={captured_sha: captured_record},
            used_fix_shas=used_fix_shas,
        )


def test_default_build_and_publish_payload_are_candidate_first(tmp_path: Path) -> None:
    checker = load_checker("check_supplemental_r3_default_publish")
    checker.handle_verify_payload = lambda **kwargs: 0
    checker.verify_journal_page_closure = lambda **kwargs: {
        "evidence_request_count": 19,
        "journal_record_count": 42,
        "journal_sha256": "8" * 64,
    }
    checker._candidate_collection_prefix_state = lambda journal: {
        "evidence_request_count": 19,
        "journal_record_count": 42,
        "journal_sha256": "8" * 64,
    }
    checker._verify_pre_network_seal_operation_completion = lambda **kwargs: None
    candidate = tmp_path / "candidate"
    payload = candidate / "data/external_slice/supplemental_r3"
    payload.mkdir(parents=True)
    for name in ("ISSUE_SNAPSHOT.json", "REVIEW_QUEUE.json"):
        (payload / name).write_text("{}\n", encoding="utf-8")
    (payload / "EVIDENCE_SNAPSHOT.json").write_text(
        json.dumps({"artifacts": []}) + "\n", encoding="utf-8"
    )
    (payload / "PAGE_MANIFESTS.json").write_text(
        json.dumps({"pages": []}) + "\n", encoding="utf-8"
    )
    rows = []
    for repo, count in checker.EXPECTED_QUOTAS.items():
        rows.extend({"repository": repo, "decision": "ADMIT_PENDING_REPRO"} for _ in range(count))
    (payload / "REVIEW_DECISIONS.json").write_text(json.dumps({"rows": rows}) + "\n", encoding="utf-8")
    (payload / "admission_sheet.cursor_candidate.csv").write_text("neutral_id\n", encoding="utf-8")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    journal = runtime / "command-journal.jsonl"
    root = tmp_path / "repository"
    seal_path = root / checker.VM_SEAL_REL
    seal_path.parent.mkdir(parents=True)
    vm_report = {
        "phase": "green",
        "vm_run": True,
        "evidence_request_count": 0,
        "records": [{"node_id": "f.py::test_node", "outcome": "PASS"}],
        "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
        "full_suite_network_spy_count": 0,
    }
    seal_path.write_text(json.dumps({
        "bundle_commit": "a" * 40,
        "bundle_tree": "b" * 40,
        "bundle_manifest_sha256": "c" * 64,
        "design_sha256": "9" * 64,
        "spool_sha256": "d" * 64,
        "plan_sha256": ["1" * 64, "2" * 64, "3" * 64, "4" * 64],
        "journal_prefix_sha256": "7" * 64,
        "journal_record_count": 20,
        "evidence_request_count": 0,
        "vm_green_report_sha256": hashlib.sha256(
            checker._common.canonical_json_bytes(vm_report) + b"\n"
        ).hexdigest(),
        "vm_green_report": vm_report,
        "vm_green": {
            "node_count": 1,
            "full_suite": {"passed": 549, "warnings": 10, "duration_seconds": 420.0},
            "evidence_request_count": 0,
        },
        "environment_seal_commit_command": list(checker.ENVIRONMENT_SEAL_COMMIT_COMMAND),
    }, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    checker._read_vm_seal_commit = lambda **kwargs: "e" * 40
    assert checker.handle_build_payload(
        root=root, candidate_root=candidate, authority="a" * 40, journal=journal,
        branch=checker.EVIDENCE_BRANCH,
    ) == 0
    manifest = payload / checker.PAYLOAD_MANIFEST
    assert manifest.is_file()
    assert json.loads(manifest.read_text(encoding="utf-8"))["pre_network_seal_commit"] == "e" * 40
    assert json.loads(manifest.read_text(encoding="utf-8"))["evidence_request_count"] == 19
    def exchange(left: Path, right: Path) -> None:
        temporary = tmp_path / "default-publish-exchange"
        left.rename(temporary)
        right.rename(left)
        temporary.rename(right)

    checker._atomic_exchange_directories = exchange
    assert checker.handle_publish_payload(
        root=root, candidate_root=candidate, authority="a" * 40, journal=journal,
        branch=checker.EVIDENCE_BRANCH,
    ) == 0
    assert (root / checker.PAYLOAD_REL / checker.PAYLOAD_MANIFEST).is_file()
    assert any(path.is_file() for path in candidate.rglob("*"))
