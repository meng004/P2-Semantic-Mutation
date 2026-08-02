"""Mocked transport tests for supplemental mining R2 (§6.1 + positive path)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
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
    assert (root / "transport_pages").is_dir()
    assert not (root / "RETRIEVAL_HARD_FAIL.json").exists()

    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    scope = json.loads((root / "SCOPE.json").read_text())
    rebuilt = miner.build_queue_from_snapshot(scope, snapshot)
    assert rebuilt == queue["records"]
    # Each repo should have exactly one phrase-matching issue in the default fixture.
    assert len(queue["records"]) == 6
    assert queue["records"][0]["neutral_id"] == "EXT-pymc-01"
    assert "wrong result" in queue["records"][0]["matched_phrases"]


def test_build_queue_pure_reconstruction(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    assert miner.cmd_retrieve(root, runner=build_complete_runner()) == 0
    (root / "REVIEW_QUEUE.json").unlink()
    assert miner.cmd_build_queue(root) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    scope = json.loads((root / "SCOPE.json").read_text())
    assert queue["records"] == miner.build_queue_from_snapshot(scope, snapshot)


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
    code = miner.cmd_retrieve(root, runner=build_complete_runner(exit_code=1))
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "nonzero_exit"


def test_malformed_json(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    first = scope_repos()[0]
    code = miner.cmd_retrieve(
        root,
        runner=build_complete_runner(
            malformed_for=(f"{first['owner']}/{first['name']}", 0)
        ),
    )
    assert_hard_fail_no_candidates(root, code)
    fail = json.loads((root / "RETRIEVAL_HARD_FAIL.json").read_text())
    assert fail["invariant"] == "malformed_json"


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
