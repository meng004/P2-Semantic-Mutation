from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path

import pytest


ROOT = Path(os.environ.get("SUPPLEMENTAL_R3_MODULE_ROOT", Path(__file__).resolve().parents[2]))


def test_environment_gate_precedes_collection_and_binds_head(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_environment_gate")
    root = tmp_path / "repository"
    seal_path = root / "data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json"
    seal_path.parent.mkdir(parents=True)
    seal_path.write_bytes(b"sealed-environment\n")
    seal_sha = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    seal_commit = "e" * 40
    journal = tmp_path / "journal.jsonl"
    operation_key = "1:verify_environment_seal"
    records = [
        {
            "sequence": 1, "stage": "operation_intent",
            "operation_name": "verify_environment_seal", "operation_key": operation_key,
            "evidence_request": False, "runner_state": "pending",
        },
        {
            "sequence": 2, "stage": "operation", "operation_key": operation_key,
            "metadata": {
                "seal_commit": seal_commit, "seal_sha256": seal_sha,
                "evidence_request_count": 0,
            },
            "evidence_request": False, "runner_state": "active",
        },
    ]
    journal.write_bytes(b"".join(
        miner._common.canonical_json_bytes(row) + b"\n" for row in records
    ))

    class Runner:
        evidence_request_count = 0

        def __init__(self):
            self.argv = []

        def run(self, argv):
            self.argv.append(list(argv))
            if argv[-2:] == ["rev-parse", "HEAD"]:
                return (seal_commit + "\n").encode(), b""
            return b"", b""

    runner = Runner()
    assert miner.verify_environment_gate_before_collection(
        root=root, journal=journal, runner=runner
    ) == {"seal_commit": seal_commit, "seal_sha256": seal_sha}
    assert runner.argv == [
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
    ]
    records.append({
        "sequence": 3, "stage": "operation_intent", "operation_name": "unexpected",
        "operation_key": "3:unexpected", "evidence_request": False, "runner_state": "pending",
    })
    journal.write_bytes(b"".join(
        miner._common.canonical_json_bytes(row) + b"\n" for row in records
    ))
    with pytest.raises(miner.GateError, match="environment_verification_boundary"):
        miner.verify_environment_gate_before_collection(
            root=root, journal=journal, runner=Runner()
        )


def test_default_execute_uses_repository_root_and_reaches_first_request(
    tmp_path: Path, monkeypatch,
) -> None:
    miner = load_miner("mine_supplemental_r3_default_root")
    repository_root = Path(__file__).resolve().parents[2]
    journal = tmp_path / "journal.jsonl"
    journal.write_text("{}\n", encoding="utf-8")
    observed = {}

    class FirstRequestReached(RuntimeError):
        pass

    class FakeRunner:
        evidence_request_count = 0

        def __init__(self, journal_path):
            observed["journal"] = Path(journal_path)

        def begin_operation(self, name, metadata):
            observed["operation"] = (name, metadata)
            return "candidate"

        def run(self, argv, *, evidence_request=False, request_key=None):
            assert evidence_request is True
            assert argv[:3] == ["gh", "api", "graphql"]
            observed["request_key"] = request_key
            raise FirstRequestReached(str(request_key))

    frozen = {
        "transport": {},
        "scope": {
            "repositories": [{
                "repository": "cornellius-gp/gpytorch", "order": 1,
            }],
        },
        "quotas": {"quota_vector": {
            "cornellius-gp/gpytorch": 2,
            "jonathf/chaospy": 3,
            "SALib/SALib": 3,
        }},
        "queries": {
            name: {"bytes": b"query Test { viewer { login } }", "sha256": "a" * 64}
            for name in ("discovery", "issue_evidence", "fix_evidence")
        },
    }

    def load_contract(path):
        observed["frozen_root"] = Path(path)
        return frozen

    def environment_gate(*, root, journal, runner):
        observed["gate_root"] = Path(root)
        return {"seal_commit": "b" * 40, "seal_sha256": "c" * 64}

    monkeypatch.setattr(miner, "load_frozen_contract", load_contract, raising=False)
    monkeypatch.setattr(
        miner, "verify_environment_gate_before_collection", environment_gate,
        raising=False,
    )
    monkeypatch.setattr(miner._common, "TerminalCommandRunner", FakeRunner)
    with pytest.raises(FirstRequestReached, match="discovery:cornellius-gp/gpytorch:0"):
        miner.execute(
            root=repository_root,
            candidate_root=tmp_path / "candidate",
            authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
            journal=journal,
        )
    assert observed["gate_root"] == repository_root
    assert observed["frozen_root"] == (
        repository_root / "data/external_slice/supplemental_r3"
    )


def load_miner(name: str = "mine_supplemental_r3"):
    path = ROOT / "scripts/external_slice/mine_supplemental_r3.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scope() -> dict:
    return {
        "created_cutoff": "2026-08-05T07:31:15Z",
        "common_phrases": ["wrong value", "overflow"],
        "repository_phrases": {"cornellius-gp/gpytorch": ["kernel value"]},
        "matching": {"surfaces": ["title", "bodyText", "complete_label_name_set"]},
        "repositories": [
            {"order": 1, "repository": "cornellius-gp/gpytorch", "id_prefix": "EXT-gpytorch-", "id_start": 6},
            {"order": 2, "repository": "jonathf/chaospy", "id_prefix": "EXT-chaospy-", "id_start": 3},
            {"order": 3, "repository": "SALib/SALib", "id_prefix": "EXT-salib-", "id_start": 1},
        ],
    }


def issue(number: int, *, repository: str = "cornellius-gp/gpytorch", title: str = "wrong value") -> dict:
    return {
        "__typename": "Issue",
        "id": f"I_{repository}_{number}",
        "number": number,
        "url": f"https://github.com/{repository}/issues/{number}",
        "state": "CLOSED",
        "title": title,
        "bodyText": "",
        "createdAt": "2026-01-01T00:00:00Z",
        "closedAt": "2026-01-02T00:00:00Z",
        "labels": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []},
    }


def test_phrase_matching_uses_only_frozen_surfaces() -> None:
    miner = load_miner()
    item = issue(7, title="Kernel VALUE gives a Wrong Value")
    assert miner.matched_phrases(item, "cornellius-gp/gpytorch", scope()) == ["wrong value", "kernel value"]


def test_discovery_page_rejects_cursor_and_total_drift() -> None:
    miner = load_miner("mine_supplemental_r3_page")
    page = {
        "data": {"repository": {"nameWithOwner": "cornellius-gp/gpytorch", "issues": {
            "totalCount": 1,
            "pageInfo": {"hasNextPage": True, "endCursor": "c1"},
            "nodes": [issue(1)],
        }}}
    }
    state = miner.validate_discovery_page(page, "cornellius-gp/gpytorch", expected_total=None, seen_cursors=set())
    assert state == {"total_count": 1, "next_cursor": "c1", "terminal": False}
    with pytest.raises(miner.GateError, match="cursor_repeat"):
        miner.validate_discovery_page(page, "cornellius-gp/gpytorch", expected_total=1, seen_cursors={"c1"})


def test_build_review_queue_excludes_collisions_and_assigns_frozen_ids() -> None:
    miner = load_miner("mine_supplemental_r3_queue")
    records = [
        {**issue(1), "repository": "cornellius-gp/gpytorch", "matched_phrases": ["wrong value"]},
        {**issue(2), "repository": "cornellius-gp/gpytorch", "matched_phrases": ["wrong value"]},
    ]
    queue = miner.build_review_queue(records, scope(), {
        "issue_urls": {"https://github.com/cornellius-gp/gpytorch/issues/1"},
        "issue_node_ids": {records[0]["id"]},
    })
    assert queue[0]["collision"] is True
    assert queue[0]["neutral_id"] == ""
    assert queue[1]["neutral_id"] == "EXT-gpytorch-06"


def test_collision_issue_number_is_repository_qualified() -> None:
    miner = load_miner("mine_supplemental_r3_repo_qualified_collision")
    records = [{
        **issue(418, repository="cornellius-gp/gpytorch"),
        "repository": "cornellius-gp/gpytorch", "matched_phrases": ["wrong value"],
    }]
    queue = miner.build_review_queue(records, scope(), {
        "issue_numbers": {418},
        "issue_urls": {"https://github.com/jonathf/chaospy/issues/418"},
        "issue_node_ids": set(),
    })
    assert queue[0]["collision"] is False


def test_repository_stops_are_independent_and_no_over_yield_moves() -> None:
    miner = load_miner("mine_supplemental_r3_stops")
    rows = []
    for repo, count in (("cornellius-gp/gpytorch", 4), ("jonathf/chaospy", 4), ("SALib/SALib", 4)):
        for index in range(count):
            rows.append({"repository": repo, "decision": "ADMIT_PENDING_REPRO", "row": index})
    result = miner.apply_repository_stops(rows, {
        "cornellius-gp/gpytorch": 2,
        "jonathf/chaospy": 3,
        "SALib/SALib": 3,
    })
    counts = {repo: sum(r["counted"] for r in result if r["repository"] == repo) for repo in {
        "cornellius-gp/gpytorch", "jonathf/chaospy", "SALib/SALib"
    }}
    assert counts == {"cornellius-gp/gpytorch": 2, "jonathf/chaospy": 3, "SALib/SALib": 3}
    assert sum(r["status"] == "NOT_REVIEWED_AFTER_STOP" for r in result) == 4


def test_graphql_runner_counts_before_call_and_forbids_retry() -> None:
    miner = load_miner("mine_supplemental_r3_graphql")
    calls = []

    def executor(argv):
        calls.append(tuple(argv))
        return (0, b'{"data":{}}', b"")

    runner = miner.GraphQLCommandRunner(executor=executor)
    runner.request("query X { viewer { login } }", {"number": 1}, request_key="page-1")
    assert runner.evidence_request_count == 1
    with pytest.raises(miner.GateError, match="duplicate_request"):
        runner.request("query X { viewer { login } }", {"number": 1}, request_key="page-1")
    assert len(calls) == 1


def test_journaled_request_uses_shared_runner_exactly_once() -> None:
    miner = load_miner("mine_supplemental_r3_journaled_request")
    calls = []

    class SpyRunner:
        def run(self, argv, *, evidence_request, request_key):
            calls.append((list(argv), evidence_request, request_key))
            return b'{"data":{}}', b""

    frozen = {"queries": {"discovery": {"bytes": b"query Frozen { viewer { login } }"}}}
    request = miner.make_journaled_request(frozen, SpyRunner())
    assert request("discovery", {"name": "gpytorch", "after": None}, "discovery:0") == b'{"data":{}}'
    assert calls == [([
        "gh", "api", "graphql", "-f", "query=query Frozen { viewer { login } }",
        "-f", "name=gpytorch",
    ], True, "discovery:0")]


def test_review_envelope_is_flushed_before_exact_schema_decision_is_read() -> None:
    miner = load_miner("mine_supplemental_r3_review_envelope")

    class Output:
        def __init__(self):
            self.text = ""
            self.flushed = False

        def write(self, value):
            self.text += value

        def flush(self):
            self.flushed = True

    output = Output()
    decision = {
        "neutral_id": "EXT-gpytorch-06", "fixed_sha": "a" * 40,
        "crit_real_public_fix": "PASS", "crit_in_numerical_scope": "PASS",
        "crit_dual_arm_repro": "PENDING", "decision": "ADMIT_PENDING_REPRO",
        "decision_reason": "public numerical fix", "exclusion_class": "",
        "mechanism": "rounding error", "analysis_id": "", "alias": "",
    }
    envelope = {
        "neutral_id": "EXT-gpytorch-06", "repository": "cornellius-gp/gpytorch",
        "issue_number": 8, "issue_url": "https://github.com/cornellius-gp/gpytorch/issues/8",
        "fix_candidates": ["a" * 40], "issue_page_sha256s": ["b" * 64],
    }
    accepted = miner.read_review_decision(
        envelope=envelope,
        input_stream=iter([json.dumps(decision) + "\n"]),
        output_stream=output,
    )
    assert output.flushed is True
    assert json.loads(output.text)["review_envelope"] == envelope

    excluded = dict(decision)
    excluded.update({
        "fixed_sha": "",
        "crit_real_public_fix": "FAIL",
        "decision": "EXCLUDED",
        "exclusion_class": "NO_VALID_PUBLIC_FIX",
    })
    miner.validate_decision_input(excluded)
    assert accepted == decision
    with pytest.raises(miner.GateError, match="decision_schema"):
        miner.validate_decision_input({**decision, "unexpected": True})


def test_frozen_contract_loader_verifies_all_three_query_hashes() -> None:
    miner = load_miner("mine_supplemental_r3_contract")
    frozen = miner.load_frozen_contract(Path(__file__).resolve().parents[2] / "data/external_slice/supplemental_r3")
    assert set(frozen["queries"]) == {"discovery", "issue_evidence", "fix_evidence"}
    assert all(len(item["sha256"]) == 64 for item in frozen["queries"].values())


def test_issue_evidence_page_advances_comments_and_timeline_independently() -> None:
    miner = load_miner("mine_supplemental_r3_issue_page")
    payload = {"data": {"repository": {"issue": {
        **issue(8),
        "comments": {"totalCount": 1, "pageInfo": {"hasNextPage": True, "endCursor": "cc1"}, "nodes": [{"id": "c1"}]},
        "timelineItems": {"totalCount": 0, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []},
    }}}}
    state = miner.validate_issue_evidence_page(
        payload,
        repository="cornellius-gp/gpytorch",
        issue_number=8,
        expected_comment_total=None,
        expected_timeline_total=None,
        seen_comment_cursors=set(),
        seen_timeline_cursors=set(),
    )
    assert state["comments_after"] == "cc1"
    assert state["timeline_after"] is None
    assert state["terminal"] is False


def test_capture_issue_evidence_continues_until_both_connections_terminate(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_issue_capture")
    calls = []

    def request(operation, variables, key):
        calls.append((operation, variables, key))
        second = variables["timelineAfter"] == "tc1"
        comments_terminal = variables["commentsAfter"] == "cc-final"
        payload = {"data": {"repository": {"issue": {
            **issue(8),
            "comments": {
                "totalCount": 1,
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None if comments_terminal else "cc-final",
                },
                "nodes": [] if comments_terminal else [{"id": "comment-1"}],
            },
            "timelineItems": {
                "totalCount": 2,
                "pageInfo": {
                    "hasNextPage": not second,
                    "endCursor": None if second else "tc1",
                },
                "nodes": [{
                    "__typename": "ClosedEvent",
                    "closer": {"__typename": "PullRequest", "mergeCommit": {"oid": ("b" if second else "a") * 40}},
                }],
            },
        }}}}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    captured = miner.capture_issue_evidence(
        request=request,
        repository="cornellius-gp/gpytorch",
        neutral_id="EXT-gpytorch-06",
        issue_number=8,
        payload_root=tmp_path,
        query_sha256="f" * 64,
    )
    assert [call[1]["commentsAfter"] for call in calls] == [None, "cc-final"]
    assert [call[1]["timelineAfter"] for call in calls] == [None, "tc1"]
    assert captured["fix_candidates"] == ["a" * 40, "b" * 40]
    assert len(captured["page_manifest"]) == 2
    assert all((tmp_path / row["path"]).is_file() for row in captured["page_manifest"])


def test_capture_issue_evidence_does_not_repeat_terminal_timeline_connection(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_timeline_terminal")
    calls = []

    def request(operation, variables, key):
        calls.append((operation, variables, key))
        comments_second = variables["commentsAfter"] == "cc1"
        timeline_terminal = variables["timelineAfter"] == "tt-final"
        payload = {"data": {"repository": {"issue": {
            **issue(8),
            "comments": {
                "totalCount": 2,
                "pageInfo": {
                    "hasNextPage": not comments_second,
                    "endCursor": None if comments_second else "cc1",
                },
                "nodes": [{"id": "c2" if comments_second else "c1"}],
            },
            "timelineItems": {
                "totalCount": 1,
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None if timeline_terminal else "tt-final",
                },
                "nodes": [] if timeline_terminal else [{
                    "__typename": "ClosedEvent",
                    "closer": {"__typename": "PullRequest", "mergeCommit": {"oid": "a" * 40}},
                }],
            },
        }}}}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    captured = miner.capture_issue_evidence(
        request=request,
        repository="cornellius-gp/gpytorch",
        neutral_id="EXT-gpytorch-06",
        issue_number=8,
        payload_root=tmp_path,
        query_sha256="f" * 64,
    )
    assert [call[1]["commentsAfter"] for call in calls] == [None, "cc1"]
    assert [call[1]["timelineAfter"] for call in calls] == [None, "tt-final"]
    assert captured["fix_candidates"] == ["a" * 40]


def test_fix_evidence_requires_commit_identity_repository_and_complete_parents() -> None:
    miner = load_miner("mine_supplemental_r3_fix")
    payload = {"data": {"repository": {"object": {
        "__typename": "Commit",
        "oid": "a" * 40,
        "url": "https://github.com/cornellius-gp/gpytorch/commit/" + "a" * 40,
        "committedDate": "2026-01-02T00:00:00Z",
        "messageHeadline": "fix wrong value",
        "repository": {"nameWithOwner": "cornellius-gp/gpytorch"},
        "parents": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"oid": "b" * 40}]},
    }}}}
    record = miner.validate_fix_evidence(payload, "cornellius-gp/gpytorch", "a" * 40)
    assert record["parents"] == ["b" * 40]
    payload["data"]["repository"]["object"]["parents"]["pageInfo"]["hasNextPage"] = True
    with pytest.raises(miner.GateError, match="incomplete_parents"):
        miner.validate_fix_evidence(payload, "cornellius-gp/gpytorch", "a" * 40)


def test_fix_evidence_only_missing_object_is_scientific_exclusion() -> None:
    miner = load_miner("mine_supplemental_r3_fix_classification")
    missing = {"data": {"repository": {"object": None}}}
    assert miner.validate_fix_evidence(
        missing, "cornellius-gp/gpytorch", "a" * 40
    ) is None
    with pytest.raises(miner.GateError, match="graphql_errors"):
        miner.validate_fix_evidence(
            {"errors": [{"message": "transport failure"}]},
            "cornellius-gp/gpytorch",
            "a" * 40,
        )
    with pytest.raises(miner.GateError, match="fix_identity"):
        miner.validate_fix_evidence(
            {"data": {"repository": None}},
            "cornellius-gp/gpytorch",
            "a" * 40,
        )


def test_admit_requires_exactly_one_noncollision_valid_fix() -> None:
    miner = load_miner("mine_supplemental_r3_unambiguous_fix")
    first = "a" * 40
    second = "b" * 40
    assert miner.unique_admissible_fix({first: {"oid": first}}, set()) == first
    assert miner.unique_admissible_fix({}, set()) is None
    assert miner.unique_admissible_fix(
        {first: {"oid": first}, second: {"oid": second}}, set()
    ) is None
    assert miner.unique_admissible_fix({first: {"oid": first}}, {first}) is None


def test_fix_candidates_are_derived_only_from_captured_timeline_prs() -> None:
    miner = load_miner("mine_supplemental_r3_candidates")
    timeline = [
        {"__typename": "ClosedEvent", "closer": {"__typename": "PullRequest", "mergeCommit": {"oid": "a" * 40}}},
        {"__typename": "CrossReferencedEvent", "source": {"__typename": "PullRequest", "mergeCommit": {"oid": "b" * 40}}},
        {"__typename": "ConnectedEvent", "subject": {"__typename": "Issue", "number": 9}},
    ]
    assert miner.extract_fix_candidates(timeline) == ["a" * 40, "b" * 40]


def test_miner_cli_has_single_execute_operation() -> None:
    miner = load_miner("mine_supplemental_r3_cli")
    parser = miner.build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert set(choices) == {"execute"}


def test_miner_main_dispatches_exact_execute_arguments(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_main")
    captured = {}

    def execute_fn(**kwargs):
        captured.update(kwargs)
        return 0

    assert miner.main([
        "execute", "--root", str(tmp_path / "root"), "--candidate-root", str(tmp_path / "candidate"),
        "--authority", "a" * 40, "--journal", str(tmp_path / "journal.jsonl"),
    ], execute_fn=execute_fn) == 0
    assert captured["authority"] == "a" * 40
    assert captured["candidate_root"] == tmp_path / "candidate"


def test_miner_main_treats_success_summary_as_zero_exit(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_main_summary")
    assert miner.main([
        "execute", "--root", str(tmp_path / "root"), "--candidate-root", str(tmp_path / "candidate"),
        "--authority", "a" * 40, "--journal", str(tmp_path / "journal.jsonl"),
    ], execute_fn=lambda **kwargs: {"quota_results": {}, "evidence_request_count": 0}) == 0


def test_execute_builds_complete_candidate_from_one_synthetic_pass(tmp_path: Path) -> None:
    miner = load_miner("mine_supplemental_r3_execute")
    repositories = {
        "cornellius-gp/gpytorch": 2,
        "jonathf/chaospy": 3,
        "SALib/SALib": 3,
    }
    issue_rows = {}
    request_keys = []
    repo_ids = {repo: index for index, repo in enumerate(repositories, start=1)}

    def fixed_sha(repo: str, number: int) -> str:
        return f'{repo_ids[repo] * 1000 + number:040x}'

    for repo, count in repositories.items():
        issue_rows[repo] = [issue(index + 1, repository=repo) for index in range(count)]

    def request_fn(operation, variables, request_key):
        request_keys.append(request_key)
        repo = f'{variables["owner"]}/{variables["name"]}'
        if operation == "discovery":
            payload = {"data": {"repository": {"nameWithOwner": repo, "issues": {
                "totalCount": len(issue_rows[repo]),
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": issue_rows[repo],
            }}}}
        elif operation == "issue_evidence":
            number = variables["number"]
            fix = fixed_sha(repo, number)
            payload = {"data": {"repository": {"nameWithOwner": repo, "issue": {
                **issue(number, repository=repo),
                "comments": {"totalCount": 0, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []},
                "timelineItems": {"totalCount": 1, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [
                    {"__typename": "ClosedEvent", "closer": {"__typename": "PullRequest", "mergeCommit": {"oid": fix}}}
                ]},
            }}}}
        else:
            oid = variables["oid"]
            payload = {"data": {"repository": {"nameWithOwner": repo, "object": {
                "__typename": "Commit", "oid": oid,
                "url": f"https://github.com/{repo}/commit/{oid}",
                "committedDate": "2026-01-02T00:00:00Z", "messageHeadline": "fix",
                "repository": {"nameWithOwner": repo},
                "parents": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"oid": "f" * 40}]},
            }}}}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    decisions = []
    prefixes = {
        "cornellius-gp/gpytorch": ("EXT-gpytorch-", 6),
        "jonathf/chaospy": ("EXT-chaospy-", 3),
        "SALib/SALib": ("EXT-salib-", 1),
    }
    for repo, rows in issue_rows.items():
        prefix, start = prefixes[repo]
        for offset, row in enumerate(rows):
            decisions.append({
                "neutral_id": f"{prefix}{start + offset:02d}",
                "fixed_sha": fixed_sha(repo, row["number"]),
                "crit_real_public_fix": "PASS",
                "crit_in_numerical_scope": "PASS",
                "crit_dual_arm_repro": "PENDING",
                "decision": "ADMIT_PENDING_REPRO",
                "decision_reason": "captured public numerical fix",
                "exclusion_class": "",
                "mechanism": "wrong numerical value",
                "analysis_id": "",
                "alias": "",
            })

    candidate = tmp_path / "candidate"

    def decision_stream():
        for decision in decisions:
            assert any(
                key.startswith(f'fix:{decision["neutral_id"]}:') for key in request_keys
            ), "fix evidence must be captured before the final decision is consumed"
            yield decision

    summary = miner.execute(
        root=Path(__file__).resolve().parents[2],
        candidate_root=candidate,
        authority="31a4a8249f4ba6de12ba92291ab0cd55a65043b4",
        journal=tmp_path / "journal.jsonl",
        request_fn=request_fn,
        decisions=decision_stream(),
    )
    assert summary["quota_results"] == repositories
    assert summary["evidence_request_count"] == 19
    payload_root = candidate / "data/external_slice/supplemental_r3"
    assert (payload_root / "REVIEW_QUEUE.json").is_file()
    assert (payload_root / "REVIEW_DECISIONS.json").is_file()
    assert (payload_root / "admission_sheet.cursor_candidate.csv").is_file()
    checker_path = Path(__file__).resolve().parents[2] / "scripts/external_slice/check_supplemental_r3_admission.py"
    checker_spec = importlib.util.spec_from_file_location("check_supplemental_r3_integrated_replay", checker_path)
    assert checker_spec is not None and checker_spec.loader is not None
    checker = importlib.util.module_from_spec(checker_spec)
    checker_spec.loader.exec_module(checker)
    assert checker.reconstruct_from_raw(
        payload_root,
        frozen_root=Path(__file__).resolve().parents[2] / "data/external_slice/supplemental_r3",
    )["quota_results"] == repositories
    frozen_root = Path(__file__).resolve().parents[2] / "data/external_slice/supplemental_r3"
    frozen = miner.load_frozen_contract(frozen_root)
    pages = json.loads((payload_root / "PAGE_MANIFESTS.json").read_text(encoding="utf-8"))["pages"]
    records = []
    operation_by_kind = {
        "discovery": "discovery", "issue": "issue_evidence", "fix": "fix_evidence"
    }
    for page in pages:
        operation = operation_by_kind[page["kind"]]
        argv = miner.graphql_argv(
            frozen["queries"][operation]["bytes"].decode("utf-8"), page["variables"]
        )
        intent_sequence = len(records) + 1
        records.extend([
            {
                "sequence": intent_sequence,
                "stage": "request_intent",
                "argv": argv,
                "evidence_request": True,
                "request_key": page["request_key"],
                "runner_state": "pending",
            },
            {
                "sequence": intent_sequence + 1,
                "stage": "command",
                "argv": argv,
                "exit_code": 0,
                "stdout_sha256": page["response_sha256"],
                "evidence_request": True,
                "request_key": page["request_key"],
                "runner_state": "active",
            },
        ])
    journal = tmp_path / "evidence-journal.jsonl"
    journal.write_bytes(b"".join(
        checker._common.canonical_json_bytes(record) + b"\n" for record in records
    ))
    closure = checker.verify_journal_page_closure(
        payload_root=payload_root, frozen_root=frozen_root, journal=journal
    )
    assert closure["evidence_request_count"] == 19
    records[1]["stdout_sha256"] = "0" * 64
    journal.write_bytes(b"".join(
        checker._common.canonical_json_bytes(record) + b"\n" for record in records
    ))
    with pytest.raises(checker.GateError, match="journal_page_binding"):
        checker.verify_journal_page_closure(
            payload_root=payload_root, frozen_root=frozen_root, journal=journal
        )
