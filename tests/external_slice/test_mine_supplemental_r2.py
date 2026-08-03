"""Mocked transport tests for supplemental mining R2 (§6.1 + positive path)."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Callable

import pytest

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "data" / "external_slice" / "supplemental_r2"
MINER_PATH = ROOT / "scripts" / "external_slice" / "mine_supplemental_r2.py"

CANDIDATE_NAMES = [
    "ISSUE_SNAPSHOT.json",
    "REVIEW_QUEUE.json",
    "REVIEW_DECISIONS.json",
    "EVIDENCE_SNAPSHOT.json",
    "admission_sheet.cursor_candidate.csv",
    "HANDOFF_SUPPLEMENTAL_R2.json",
    "PUBLISH_COMMIT.json",
    "transport_pages",
    "admission_evidence",
]


def load_miner():
    spec = importlib.util.spec_from_file_location("mine_supplemental_r2", MINER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


miner = load_miner()

FIXED_CODE_COMMIT = "a" * 40


@pytest.fixture
def bind_code_commit(monkeypatch: pytest.MonkeyPatch):
    """Force retrieve code_commit to a stable full SHA for deterministic tests."""

    def _bind(sha: str = FIXED_CODE_COMMIT) -> str:
        monkeypatch.setattr(miner, "current_checkout_code_commit", lambda: sha)
        return sha

    return _bind


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def seed_root(tmp_path: Path) -> Path:
    root = tmp_path / "supplemental_r2"
    root.mkdir(parents=True)
    for name in ("SCOPE.json", "TRANSPORT_CONTRACT.json", "QUOTAS.json"):
        shutil.copy2(FROZEN / name, root / name)
    return root


def candidate_artifacts(root: Path) -> list[str]:
    found = []
    for name in CANDIDATE_NAMES:
        path = root / name
        if path.exists():
            found.append(name)
    return found


def make_issue(
    *,
    number: int,
    owner: str,
    name: str,
    created_at: str,
    title: str,
    body: str = "",
    labels: list[str] | None = None,
    state: str = "CLOSED",
    closed_at: str | None = "2026-01-02T00:00:00Z",
    typename: str = "Issue",
    url: str | None = None,
) -> dict[str, Any]:
    return {
        "__typename": typename,
        "id": f"ISSUE_{owner}_{name}_{number}",
        "number": number,
        "url": url or f"https://github.com/{owner}/{name}/issues/{number}",
        "state": state,
        "title": title,
        "bodyText": body,
        "createdAt": created_at,
        "updatedAt": created_at,
        "closedAt": closed_at,
        "labels": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"name": lab} for lab in (labels or [])],
        },
    }


def make_page(
    *,
    owner: str,
    name: str,
    nodes: list[dict[str, Any]],
    total_count: int | None = None,
    has_next: bool = False,
    end_cursor: str | None = None,
    errors: list[Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "data": {
            "repository": {
                "issues": {
                    "totalCount": total_count if total_count is not None else len(nodes),
                    "pageInfo": {
                        "hasNextPage": has_next,
                        "endCursor": end_cursor,
                    },
                    "nodes": nodes,
                }
            }
        }
    }
    if errors is not None:
        payload["errors"] = errors
    return payload


def scope_repos() -> list[dict[str, Any]]:
    return json.loads((FROZEN / "SCOPE.json").read_text())["repositories"]


def build_complete_runner(
    mutator: Callable[[str, int, dict[str, Any]], dict[str, Any] | None] | None = None,
    *,
    per_repo_issues: dict[str, list[dict[str, Any]]] | None = None,
    exit_code: int = 0,
    malformed_for: tuple[str, int] | None = None,
) -> Callable[[str, dict[str, Any]], tuple[int, str, str]]:
    """Return a GraphQL runner serving one terminal page per repo by default."""

    pages: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for repo in scope_repos():
        key = (repo["owner"], repo["name"])
        if per_repo_issues and repo["repo"] in per_repo_issues:
            nodes = per_repo_issues[repo["repo"]]
        else:
            # Two closed issues; first matches phrase, second does not.
            nodes = [
                make_issue(
                    number=10,
                    owner=repo["owner"],
                    name=repo["name"],
                    created_at="2025-06-01T00:00:00Z",
                    title="wrong result in kernel",
                    body="numerical issue",
                    labels=["bug"],
                ),
                make_issue(
                    number=9,
                    owner=repo["owner"],
                    name=repo["name"],
                    created_at="2025-05-01T00:00:00Z",
                    title="docs typo",
                    body="documentation only",
                ),
            ]
        page = make_page(
            owner=repo["owner"],
            name=repo["name"],
            nodes=nodes,
            total_count=len(nodes),
            has_next=False,
            end_cursor="CURSOR_END",
        )
        pages[key] = [page]

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        owner = variables["owner"]
        name = variables["name"]
        after = variables.get("after")
        key = (owner, name)
        repo_pages = pages[key]
        # Single-page default: after must be None.
        index = 0 if after is None else 1
        if index >= len(repo_pages):
            return 1, "", "no such page"
        payload = json.loads(json.dumps(repo_pages[index]))
        if mutator is not None:
            mutated = mutator(f"{owner}/{name}", index, payload)
            if mutated is None:
                return exit_code, "", "mutator aborted"
            payload = mutated
        if malformed_for == (f"{owner}/{name}", index):
            return exit_code, "{not-json", ""
        stdout = json.dumps(payload)
        return exit_code, stdout, ""

    return runner


def build_multipage_runner(
    *,
    mutate: Callable[[list[dict[str, Any]]], list[dict[str, Any]]] | None = None,
) -> Callable[[str, dict[str, Any]], tuple[int, str, str]]:
    """Two-page runner for the first repository; one page for others."""
    repos = scope_repos()
    first = repos[0]
    nodes_p0 = [
        make_issue(
            number=20,
            owner=first["owner"],
            name=first["name"],
            created_at="2025-07-01T00:00:00Z",
            title="wrong result A",
        ),
        make_issue(
            number=19,
            owner=first["owner"],
            name=first["name"],
            created_at="2025-06-15T00:00:00Z",
            title="incorrect value B",
        ),
    ]
    nodes_p1 = [
        make_issue(
            number=18,
            owner=first["owner"],
            name=first["name"],
            created_at="2025-05-01T00:00:00Z",
            title="precision loss C",
        ),
    ]
    first_pages = [
        make_page(
            owner=first["owner"],
            name=first["name"],
            nodes=nodes_p0,
            total_count=3,
            has_next=True,
            end_cursor="C1",
        ),
        make_page(
            owner=first["owner"],
            name=first["name"],
            nodes=nodes_p1,
            total_count=3,
            has_next=False,
            end_cursor="C2",
        ),
    ]
    if mutate is not None:
        first_pages = mutate(first_pages)

    other_pages: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for repo in repos[1:]:
        nodes = [
            make_issue(
                number=10,
                owner=repo["owner"],
                name=repo["name"],
                created_at="2025-06-01T00:00:00Z",
                title="wrong result",
            )
        ]
        other_pages[(repo["owner"], repo["name"])] = [
            make_page(
                owner=repo["owner"],
                name=repo["name"],
                nodes=nodes,
                total_count=1,
                has_next=False,
                end_cursor="E",
            )
        ]

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        owner = variables["owner"]
        name = variables["name"]
        after = variables.get("after")
        if (owner, name) == (first["owner"], first["name"]):
            if after is None:
                page = first_pages[0]
            elif after == first_pages[0]["data"]["repository"]["issues"]["pageInfo"][
                "endCursor"
            ]:
                page = first_pages[1]
            else:
                return 1, "", f"wrong after {after}"
        else:
            pages = other_pages[(owner, name)]
            if after is not None:
                return 1, "", "unexpected after"
            page = pages[0]
        return 0, json.dumps(page), ""

    return runner


def assert_hard_fail_no_candidates(root: Path, code: int) -> None:
    assert code != 0
    assert (root / "RETRIEVAL_HARD_FAIL.json").is_file()
    assert (root / "COMMAND_LOG.json").is_file()
    assert candidate_artifacts(root) == []


def test_positive_retrieve_builds_snapshot_and_queue(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    runner = build_complete_runner()
    code = miner.cmd_retrieve(root, runner=runner)
    assert code == 0
    assert (root / "ISSUE_SNAPSHOT.json").is_file()
    assert (root / "REVIEW_QUEUE.json").is_file()
    assert (root / "PUBLISH_COMMIT.json").is_file()
    assert (root / "transport_pages").is_dir()
    assert not (root / "RETRIEVAL_HARD_FAIL.json").exists()

    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    publish = json.loads((root / "PUBLISH_COMMIT.json").read_text())
    scope = json.loads((root / "SCOPE.json").read_text())
    rebuilt = miner.build_queue_from_snapshot(scope, snapshot)
    assert rebuilt == queue["records"]
    # Each repo should have exactly one phrase-matching issue in the default fixture.
    assert len(queue["records"]) == 6
    assert queue["records"][0]["neutral_id"] == "EXT-pymc-01"
    assert "wrong result" in queue["records"][0]["matched_phrases"]
    page_files = {
        p.relative_to(root).as_posix(): miner.sha256_file(p)
        for p in sorted((root / "transport_pages").glob("*.json"))
    }
    expected = miner.build_publish_commit_identity(
        run_id=snapshot["run_id"],
        code_commit=snapshot["code_commit"],
        snapshot=snapshot,
        transport_page_sha256=page_files,
    )
    assert publish == expected


def test_build_queue_pure_reconstruction(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    code_commit = bind_code_commit("e" * 40)
    root = seed_root(tmp_path)
    assert miner.cmd_retrieve(
        root,
        runner=build_complete_runner(),
        run_id="rebuild-run",
        code_commit=code_commit,
    ) == 0
    (root / "REVIEW_QUEUE.json").unlink()
    assert miner.cmd_build_queue(root) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    scope = json.loads((root / "SCOPE.json").read_text())
    assert queue["records"] == miner.build_queue_from_snapshot(scope, snapshot)
    assert queue["run_id"] == "rebuild-run"
    assert queue["code_commit"] == code_commit
    assert queue["run_id"] == snapshot["run_id"]
    assert queue["code_commit"] == snapshot["code_commit"]


@pytest.mark.parametrize(
    "name,mutator",
    [
        (
            "typename_pr",
            lambda repo, idx, p: _set_node_field(p, "__typename", "PullRequest"),
        ),
        (
            "pull_url",
            lambda repo, idx, p: _set_node_field(
                p,
                "url",
                p["data"]["repository"]["issues"]["nodes"][0]["url"].replace(
                    "/issues/", "/pull/"
                ),
            ),
        ),
        (
            "state_open",
            lambda repo, idx, p: _set_node_field(p, "state", "OPEN"),
        ),
        (
            "null_closed_at",
            lambda repo, idx, p: _set_node_field(p, "closedAt", None),
        ),
        (
            "incomplete_labels",
            lambda repo, idx, p: _set_label_has_next(p, True),
        ),
        (
            "graphql_errors",
            lambda repo, idx, p: {**p, "errors": [{"message": "boom"}]},
        ),
        (
            "null_repository",
            lambda repo, idx, p: {"data": {"repository": None}},
        ),
        (
            "final_has_next",
            lambda repo, idx, p: _set_has_next(p, True, end="KEEP"),
        ),
        (
            "changed_total_count",
            lambda repo, idx, p: _set_total(p, 999),
        ),
    ],
)
def test_transport_node_negatives(tmp_path: Path, name: str, mutator) -> None:
    root = seed_root(tmp_path)
    # Mutate only the first repo page to keep failure deterministic.
    first_repo = scope_repos()[0]["repo"]

    def wrapped(repo: str, idx: int, payload: dict[str, Any]):
        if repo == first_repo and idx == 0:
            return mutator(repo, idx, payload)
        return payload

    code = miner.cmd_retrieve(root, runner=build_complete_runner(wrapped))
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"]


def _set_node_field(payload: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
    payload["data"]["repository"]["issues"]["nodes"][0][field] = value
    return payload


def _set_label_has_next(payload: dict[str, Any], value: bool) -> dict[str, Any]:
    payload["data"]["repository"]["issues"]["nodes"][0]["labels"]["pageInfo"][
        "hasNextPage"
    ] = value
    return payload


def _set_has_next(payload: dict[str, Any], value: bool, end: str = "X") -> dict[str, Any]:
    payload["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"] = value
    if value and not payload["data"]["repository"]["issues"]["pageInfo"].get("endCursor"):
        payload["data"]["repository"]["issues"]["pageInfo"]["endCursor"] = end
    return payload


def _set_total(payload: dict[str, Any], total: int) -> dict[str, Any]:
    payload["data"]["repository"]["issues"]["totalCount"] = total
    return payload


def test_command_exit_nonzero(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    calls: list[int] = []
    base = build_complete_runner(exit_code=1)

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        calls.append(1)
        return base(query, variables)

    code = miner.cmd_retrieve(root, runner=runner)
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "nonzero_exit"
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    page_entries = [e for e in log["entries"] if isinstance(e.get("page_index"), int)]
    assert len(page_entries) == len(calls) == 1
    assert page_entries[0]["page_ok"] is False
    assert page_entries[0]["invariant"] == "nonzero_exit"


def test_malformed_json(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    first = scope_repos()[0]
    calls: list[int] = []
    base = build_complete_runner(
        malformed_for=(f"{first['owner']}/{first['name']}", 0)
    )

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        calls.append(1)
        return base(query, variables)

    code = miner.cmd_retrieve(root, runner=runner)
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "malformed_json"
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    page_entries = [e for e in log["entries"] if isinstance(e.get("page_index"), int)]
    assert len(page_entries) == len(calls) == 1
    assert page_entries[0]["page_ok"] is False
    assert page_entries[0]["invariant"] == "malformed_json"


def test_middle_page_removed(tmp_path: Path) -> None:
    root = seed_root(tmp_path)

    def mutate(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Drop second page but leave hasNext on first true → incomplete.
        return [pages[0]]

    code = miner.cmd_retrieve(root, runner=build_multipage_runner(mutate=mutate))
    assert_hard_fail_no_candidates(root, code)


def test_repeated_cursor(tmp_path: Path) -> None:
    root = seed_root(tmp_path)

    def mutate(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pages = json.loads(json.dumps(pages))
        pages[1]["data"]["repository"]["issues"]["pageInfo"]["endCursor"] = pages[0][
            "data"
        ]["repository"]["issues"]["pageInfo"]["endCursor"]
        return pages

    code = miner.cmd_retrieve(root, runner=build_multipage_runner(mutate=mutate))
    assert_hard_fail_no_candidates(root, code)


def test_wrong_after_cursor(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    base = build_multipage_runner()

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        # Simulate a client that sends a wrong after on page 2.
        if variables.get("after") == "C1":
            variables = dict(variables)
            variables["after"] = "WRONG_AFTER"
        # Underlying runner only accepts the real cursor.
        owner = variables["owner"]
        name = variables["name"]
        after = variables.get("after")
        first = scope_repos()[0]
        if (owner, name) == (first["owner"], first["name"]) and after not in (None, "C1"):
            raise miner.HardFail("cursor_drift", f"wrong after {after}")
        return base(query, variables)

    code = miner.cmd_retrieve(root, runner=runner)
    assert_hard_fail_no_candidates(root, code)


def test_inconsistent_total_count_across_pages(tmp_path: Path) -> None:
    root = seed_root(tmp_path)

    def mutate(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pages = json.loads(json.dumps(pages))
        pages[1]["data"]["repository"]["issues"]["totalCount"] = 99
        return pages

    code = miner.cmd_retrieve(root, runner=build_multipage_runner(mutate=mutate))
    assert_hard_fail_no_candidates(root, code)


def test_query_document_identity_drift(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    contract = json.loads((root / "TRANSPORT_CONTRACT.json").read_text())
    contract["query_document"] = contract["query_document"].replace("first: 100", "first: 99")
    _write_json(root / "TRANSPORT_CONTRACT.json", contract)
    code = miner.cmd_retrieve(root, runner=build_complete_runner())
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "query_identity_drift"


def test_operation_name_drift(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    contract = json.loads((root / "TRANSPORT_CONTRACT.json").read_text())
    contract["operation_name"] = "Tampered"
    _write_json(root / "TRANSPORT_CONTRACT.json", contract)
    code = miner.cmd_retrieve(root, runner=build_complete_runner())
    assert_hard_fail_no_candidates(root, code)


def test_page_size_drift(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    contract = json.loads((root / "TRANSPORT_CONTRACT.json").read_text())
    contract["page_size"] = 50
    _write_json(root / "TRANSPORT_CONTRACT.json", contract)
    code = miner.cmd_retrieve(root, runner=build_complete_runner())
    assert_hard_fail_no_candidates(root, code)


def test_cutoff_drift(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    contract = json.loads((root / "TRANSPORT_CONTRACT.json").read_text())
    contract["created_cutoff"] = "2025-01-01T00:00:00Z"
    _write_json(root / "TRANSPORT_CONTRACT.json", contract)
    code = miner.cmd_retrieve(root, runner=build_complete_runner())
    assert_hard_fail_no_candidates(root, code)


def test_forbidden_transport_in_runner_command(tmp_path: Path) -> None:
    root = seed_root(tmp_path)

    def bad_runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        miner.refuse_forbidden_transport("gh search issues wrong result")
        return 0, "{}", ""

    code = miner.cmd_retrieve(root, runner=bad_runner)
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "forbidden_transport"


@pytest.mark.parametrize(
    "needle",
    [
        "/search/issues",
        "gh search",
        "search(",
        "/repos/pymc-devs/pymc/issues",
        "pr-to-issue",
    ],
)
def test_forbidden_transport_patterns(needle: str) -> None:
    with pytest.raises(miner.HardFail) as exc:
        miner.refuse_forbidden_transport(f"calling {needle} now")
    assert exc.value.invariant == "forbidden_transport"


def test_phrase_union_and_ordering(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    repo = scope_repos()[0]
    issues = [
        make_issue(
            number=3,
            owner=repo["owner"],
            name=repo["name"],
            created_at="2025-08-01T00:00:00Z",
            title="accuracy regression",
        ),
        make_issue(
            number=5,
            owner=repo["owner"],
            name=repo["name"],
            created_at="2025-08-01T00:00:00Z",
            title="wrong result",
        ),
        make_issue(
            number=4,
            owner=repo["owner"],
            name=repo["name"],
            created_at="2025-07-01T00:00:00Z",
            title="wrong result and incorrect value",
        ),
        make_issue(
            number=100,
            owner=repo["owner"],
            name=repo["name"],
            created_at="2026-08-02T00:00:00Z",
            title="wrong result after cutoff",
        ),
    ]
    per = {r["repo"]: [
        make_issue(
            number=1,
            owner=r["owner"],
            name=r["name"],
            created_at="2025-01-01T00:00:00Z",
            title="wrong result",
        )
    ] for r in scope_repos()}
    per[repo["repo"]] = issues
    code = miner.cmd_retrieve(root, runner=build_complete_runner(per_repo_issues=per))
    assert code == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())["records"]
    pymc = [r for r in queue if r["repository"] == repo["repo"]]
    # cutoff excludes #100; order by created desc then number desc: #5, #3, #4
    assert [r["issue_number"] for r in pymc] == [5, 3, 4]
    assert [r["neutral_id"] for r in pymc] == [
        "EXT-pymc-01",
        "EXT-pymc-02",
        "EXT-pymc-03",
    ]


def test_credentials_scrubbed_from_command_log(tmp_path: Path) -> None:
    root = seed_root(tmp_path)

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        base = build_complete_runner()
        code, stdout, _ = base(query, variables)
        return code, stdout, "Authorization: Bearer ghp_abcdefghijklmnopqrstuvwxyz0123456789"

    assert miner.cmd_retrieve(root, runner=runner) == 0
    log = (root / "COMMAND_LOG.json").read_text()
    assert "ghp_" not in log
    assert "Bearer ghp_" not in log


def test_hard_fail_does_not_mint_snapshot(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    # Pre-create a stale snapshot; hard fail must remove candidate artifacts.
    _write_json(root / "ISSUE_SNAPSHOT.json", {"records": []})
    code = miner.cmd_retrieve(root, runner=build_complete_runner(exit_code=1))
    assert_hard_fail_no_candidates(root, code)


def test_concurrent_retrieve_second_process_zero_network(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    code_commit = bind_code_commit("c" * 40)
    root = seed_root(tmp_path)
    prior_log = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "entries": [{"keep": True, "idx": i} for i in range(3)],
    }
    _write_json(root / "COMMAND_LOG.json", prior_log)
    _write_json(
        root / "ISSUE_SNAPSHOT.json",
        {"schema_version": 1, "records": [{"keep": True}]},
    )
    (root / "transport_pages").mkdir()
    (root / "transport_pages" / "keep.json").write_text("{}\n", encoding="utf-8")
    holder = miner.RetrieveLock(root)
    holder.acquire()
    calls: list[int] = []

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        calls.append(1)
        return 0, "{}", ""

    before_names = sorted(p.name for p in root.iterdir())
    before_log = (root / "COMMAND_LOG.json").read_bytes()
    before_snap = (root / "ISSUE_SNAPSHOT.json").read_bytes()
    before_page = (root / "transport_pages" / "keep.json").read_bytes()
    code = miner.cmd_retrieve(
        root,
        runner=runner,
        run_id="lock-run",
        code_commit=code_commit,
    )
    holder.release()
    assert code == 1
    assert calls == []
    # Lock loser: zero filesystem mutations on owner artifacts.
    assert sorted(p.name for p in root.iterdir()) == before_names
    assert (root / "COMMAND_LOG.json").read_bytes() == before_log
    assert (root / "ISSUE_SNAPSHOT.json").read_bytes() == before_snap
    assert (root / "transport_pages" / "keep.json").read_bytes() == before_page
    assert not (root / "RETRIEVAL_HARD_FAIL.json").exists()
    assert not (root / ".publish_staging").exists()
    kept = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    assert kept == prior_log
    assert candidate_artifacts(root) == ["ISSUE_SNAPSHOT.json", "transport_pages"]


def test_atomic_command_log_rejects_partial_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = seed_root(tmp_path)
    path = root / "COMMAND_LOG.json"
    miner.init_command_log(path, run_id="atomic-run", code_commit="a" * 40)
    miner.append_command_log(
        path,
        {"label": "ok", "exit_code": 0},
        run_id="atomic-run",
        code_commit="a" * 40,
    )
    before = path.read_text(encoding="utf-8")

    def boom_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        # Leave a truncated sibling temp; destination must stay intact.
        Path(src).write_text("{truncated", encoding="utf-8")
        raise OSError("simulated crash before replace")

    monkeypatch.setattr(os, "replace", boom_replace)
    with pytest.raises(OSError, match="simulated crash"):
        miner.append_command_log(
            path,
            {"label": "should-not-land", "exit_code": 0},
            run_id="atomic-run",
            code_commit="a" * 40,
        )

    assert path.read_text(encoding="utf-8") == before
    payload = json.loads(before)
    assert payload["run_id"] == "atomic-run"
    assert [e["label"] for e in payload["entries"]] == ["ok"]
    assert not path.read_text(encoding="utf-8").startswith("{truncated")


def test_generic_exception_full_cleanup_and_terminal(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    code_commit = bind_code_commit("b" * 40)
    root = seed_root(tmp_path)
    _write_json(root / "ISSUE_SNAPSHOT.json", {"records": []})
    _write_json(root / "REVIEW_QUEUE.json", {"records": []})
    (root / "transport_pages").mkdir()
    (root / "transport_pages" / "x.json").write_text("{}\n", encoding="utf-8")
    (root / "admission_evidence").mkdir()
    _write_json(
        root / "admission_evidence" / "EXT-pymc-01" / "evidence.json",
        {"neutral_id": "EXT-pymc-01"},
    )

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        raise RuntimeError("injected generic failure")

    code = miner.cmd_retrieve(
        root,
        runner=runner,
        run_id="gen-run",
        code_commit=code_commit,
    )
    assert code == 1
    assert candidate_artifacts(root) == []
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text(encoding="utf-8"))
    assert fail["invariant"] == "unexpected_error"
    assert "injected generic failure" in fail["detail"]
    assert fail["run_id"] == "gen-run"
    assert fail["code_commit"] == code_commit
    assert fail["terminal"] is True
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    assert log["run_id"] == "gen-run"
    assert log["code_commit"] == code_commit
    labels = [e.get("label") for e in log["entries"]]
    assert "retrieve_terminal_failure" in labels
    terminal = next(
        e for e in log["entries"] if e.get("label") == "retrieve_terminal_failure"
    )
    assert terminal["run_id"] == "gen-run"
    assert terminal["code_commit"] == code_commit
    assert terminal["terminal"] is True


def test_run_and_code_commit_binding_on_success(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    code_commit = bind_code_commit("d" * 40)
    root = seed_root(tmp_path)
    code = miner.cmd_retrieve(
        root,
        runner=build_complete_runner(),
        run_id="ok-run",
        code_commit=code_commit,
    )
    assert code == 0
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    assert log["run_id"] == "ok-run"
    assert log["code_commit"] == code_commit
    assert all(e.get("run_id") == "ok-run" for e in log["entries"])
    assert all(e.get("code_commit") == code_commit for e in log["entries"])
    page_entries = [
        e
        for e in log["entries"]
        if isinstance(e.get("page_index"), int) and e.get("exit_code") == 0
    ]
    assert page_entries
    assert all("endCursor" in e for e in page_entries)
    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    assert snapshot["run_id"] == "ok-run"
    assert snapshot["code_commit"] == code_commit
    assert queue["run_id"] == "ok-run"
    assert queue["code_commit"] == code_commit


def test_code_commit_must_match_checkout(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    bind_code_commit("1" * 40)
    root = seed_root(tmp_path)
    calls: list[int] = []

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        calls.append(1)
        return 0, "{}", ""

    code = miner.cmd_retrieve(
        root,
        runner=runner,
        run_id="conflict-run",
        code_commit="2" * 40,
    )
    assert code == 1
    assert calls == []
    assert not (root / "COMMAND_LOG.json").exists()
    assert not (root / "RETRIEVAL_HARD_FAIL.json").exists()
    assert candidate_artifacts(root) == []


def test_illegal_code_commit_rejected(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    bind_code_commit("not-a-full-sha")
    root = seed_root(tmp_path)
    code = miner.cmd_retrieve(root, runner=build_complete_runner(), run_id="bad-code")
    assert code == 1
    assert not (root / "COMMAND_LOG.json").exists()
    assert candidate_artifacts(root) == []


def test_append_command_log_rejects_run_code_conflict(tmp_path: Path) -> None:
    path = tmp_path / "COMMAND_LOG.json"
    miner.init_command_log(path, run_id="run-a", code_commit="a" * 40)
    with pytest.raises(miner.HardFail, match="run_id_conflict"):
        miner.append_command_log(
            path,
            {"label": "x", "exit_code": 0},
            run_id="run-b",
            code_commit="a" * 40,
        )
    with pytest.raises(miner.HardFail, match="code_commit_conflict"):
        miner.append_command_log(
            path,
            {"label": "y", "exit_code": 0, "code_commit": "b" * 40},
            run_id="run-a",
            code_commit="a" * 40,
        )


def test_crash_safe_publish_and_failure_recovery(
    tmp_path: Path, bind_code_commit: Any
) -> None:
    code_commit = bind_code_commit("f" * 40)
    root = seed_root(tmp_path)

    # Orphan staging from a prior crash must be cleared by a successful owner run.
    orphan = root / ".publish_staging" / "old-run"
    orphan.mkdir(parents=True)
    (orphan / "leftover.json").write_text("{}\n", encoding="utf-8")
    assert miner.cmd_retrieve(
        root,
        runner=build_complete_runner(),
        run_id="recover-run",
        code_commit=code_commit,
    ) == 0
    assert not (root / ".publish_staging").exists()
    assert (root / "ISSUE_SNAPSHOT.json").is_file()
    assert (root / "PUBLISH_COMMIT.json").is_file()
    assert (root / "transport_pages").is_dir()


def _run_retrieve_subprocess(
    root: Path,
    *,
    run_id: str,
    code_commit: str,
    death_at: str | None,
) -> subprocess.CompletedProcess[str]:
    script = textwrap.dedent(
        f"""
        import importlib.util
        import json
        import os
        import sys
        from pathlib import Path

        root = Path({str(root)!r})
        miner_path = Path({str(MINER_PATH)!r})
        frozen = Path({str(FROZEN)!r})
        spec = importlib.util.spec_from_file_location("mine_supplemental_r2", miner_path)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        mod.current_checkout_code_commit = lambda: {code_commit!r}

        scope = json.loads((frozen / "SCOPE.json").read_text())
        # Minimal complete fixture runner (one closed matching issue per repo).
        pages = {{}}
        for repo in scope["repositories"]:
            owner, name = repo["owner"], repo["name"]
            pages[(owner, name)] = {{
                "data": {{
                    "repository": {{
                        "issues": {{
                            "totalCount": 1,
                            "pageInfo": {{"hasNextPage": False, "endCursor": "E"}},
                            "nodes": [{{
                                "__typename": "Issue",
                                "id": f"ISSUE_{{owner}}_{{name}}_10",
                                "number": 10,
                                "url": f"https://github.com/{{owner}}/{{name}}/issues/10",
                                "state": "CLOSED",
                                "title": "wrong result",
                                "bodyText": "",
                                "createdAt": "2025-06-01T00:00:00Z",
                                "updatedAt": "2025-06-01T00:00:00Z",
                                "closedAt": "2026-01-02T00:00:00Z",
                                "labels": {{
                                    "pageInfo": {{"hasNextPage": False, "endCursor": None}},
                                    "nodes": [],
                                }},
                            }}],
                        }}
                    }}
                }}
            }}

        def runner(query, variables):
            key = (variables["owner"], variables["name"])
            return 0, json.dumps(pages[key]), ""

        if {death_at!r}:
            os.environ[{miner.PUBLISH_DEATH_ENV!r}] = {death_at!r}
        else:
            os.environ.pop({miner.PUBLISH_DEATH_ENV!r}, None)
        raise SystemExit(
            mod.cmd_retrieve(
                root,
                runner=runner,
                run_id={run_id!r},
                code_commit={code_commit!r},
            )
        )
        """
    )
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("boundary", list(miner.PUBLISH_DEATH_BOUNDARIES))
def test_publish_boundary_os_exit_death_and_recovery(
    tmp_path: Path, bind_code_commit: Any, boundary: str
) -> None:
    code_commit = bind_code_commit("9" * 40)
    root = seed_root(tmp_path / boundary)
    dead = _run_retrieve_subprocess(
        root, run_id=f"die-{boundary}", code_commit=code_commit, death_at=boundary
    )
    assert dead.returncode == 70, dead.stderr

    publish_path = root / "PUBLISH_COMMIT.json"
    if boundary in {"after_publish_commit", "after_cleanup"}:
        # Identity already sealed; leftovers may remain until recovery.
        assert publish_path.is_file()
    else:
        # Sequential artifacts without the seal must not count as complete.
        assert not publish_path.exists()

    recovered = _run_retrieve_subprocess(
        root, run_id=f"recover-{boundary}", code_commit=code_commit, death_at=None
    )
    assert recovered.returncode == 0, recovered.stderr
    assert (root / "PUBLISH_COMMIT.json").is_file()
    assert (root / "ISSUE_SNAPSHOT.json").is_file()
    assert (root / "REVIEW_QUEUE.json").is_file()
    assert (root / "transport_pages").is_dir()
    assert not (root / "RETRIEVAL_HARD_FAIL.json").exists()
    assert not list(root.glob(".transport_pages.*"))
    assert not (root / ".publish_staging").exists()
    publish = json.loads((root / "PUBLISH_COMMIT.json").read_text(encoding="utf-8"))
    assert publish["run_id"] == f"recover-{boundary}"
    assert publish["code_commit"] == code_commit


def test_validation_failure_emits_one_page_record(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    calls: list[int] = []

    def mutator(repo: str, idx: int, page: dict[str, Any]) -> dict[str, Any]:
        return _set_node_field(page, "__typename", "PullRequest")

    base = build_complete_runner(mutator=mutator)

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        calls.append(1)
        return base(query, variables)

    code = miner.cmd_retrieve(root, runner=runner)
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text(encoding="utf-8"))
    assert fail["invariant"] == "typename_not_issue"
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    page_entries = [e for e in log["entries"] if isinstance(e.get("page_index"), int)]
    assert len(page_entries) == len(calls) == 1
    assert page_entries[0]["page_ok"] is False
    assert page_entries[0]["invariant"] == "typename_not_issue"
    assert "endCursor" not in page_entries[0]


def test_seal_failed_run_archive_write_once(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    log = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "entries": [{"page_index": i, "exit_code": 0} for i in range(3)],
    }
    diag = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "invariant": "unexpected_error",
        "detail": "boom",
        "timestamp_utc": "2026-08-02T14:14:29Z",
    }
    _write_json(root / "COMMAND_LOG.json", log)
    _write_json(root / "RETRIEVAL_HARD_FAIL.json", diag)
    archive_id = "20260802T141429Z_unexpected_error"
    dest = miner.seal_failed_run_archive(root, archive_id=archive_id)
    assert dest == root / "failed_runs" / archive_id
    manifest = json.loads((dest / "ARCHIVE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["sealed"] is True
    assert manifest["write_once"] is True
    assert manifest["artifacts"]["COMMAND_LOG.json"]["entry_count"] == 3
    assert manifest["artifacts"]["COMMAND_LOG.json"]["sha256"] == miner.sha256_file(
        dest / "COMMAND_LOG.json"
    )
    assert manifest["artifacts"]["RETRIEVAL_HARD_FAIL.json"]["sha256"] == (
        miner.sha256_file(dest / "RETRIEVAL_HARD_FAIL.json")
    )
    # Live originals remain; archive is a sealed copy.
    assert (root / "COMMAND_LOG.json").is_file()
    with pytest.raises(miner.HardFail, match="archive_exists"):
        miner.seal_failed_run_archive(root, archive_id=archive_id)
