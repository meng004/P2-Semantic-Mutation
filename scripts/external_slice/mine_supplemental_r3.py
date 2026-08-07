#!/usr/bin/env python3
"""Frozen Supplemental R3 transport and deterministic screening primitives."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


def _load_common():
    path = Path(__file__).with_name("supplemental_r3_common.py")
    spec = importlib.util.spec_from_file_location("_supplemental_r3_common_miner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load supplemental_r3_common")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_common()
GateError = _common.GateError


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_frozen_contract(root: Path) -> dict[str, Any]:
    base = Path(root)
    transport = json.loads((base / "TRANSPORT_CONTRACT.json").read_text(encoding="utf-8"))
    scope_payload = json.loads((base / "SCOPE.json").read_text(encoding="utf-8"))
    quota_payload = json.loads((base / "QUOTAS.json").read_text(encoding="utf-8"))
    if transport.get("protocol") != "SUPPLEMENTAL_R3_EVIDENCE":
        raise GateError("transport_protocol")
    queries: dict[str, dict[str, Any]] = {}
    for name, record in transport.get("query_files", {}).items():
        path = Path(record["path"])
        if not path.is_absolute():
            repo_root = base.parents[2]
            path = repo_root / path
        raw = path.read_bytes()
        actual = _sha256(raw)
        if actual != record.get("sha256"):
            raise GateError(f"query_identity_drift: {name}")
        queries[name] = {"path": path, "sha256": actual, "bytes": raw}
    if set(queries) != {"discovery", "issue_evidence", "fix_evidence"}:
        raise GateError("query_set")
    return {"transport": transport, "scope": scope_payload, "quotas": quota_payload, "queries": queries}


def normalize_match_text(value: str) -> str:
    return unicodedata.normalize("NFC", value or "").casefold()


def matched_phrases(issue: dict[str, Any], repository: str, scope: dict[str, Any]) -> list[str]:
    labels = issue.get("labels", {}).get("nodes", [])
    surfaces = {
        "title": issue.get("title", ""),
        "bodyText": issue.get("bodyText", ""),
        "complete_label_name_set": "\n".join(str(item.get("name", "")) for item in labels),
    }
    allowed = scope.get("matching", {}).get("surfaces", [])
    haystacks = [normalize_match_text(surfaces[name]) for name in allowed]
    ordered = list(scope.get("common_phrases", [])) + list(
        scope.get("repository_phrases", {}).get(repository, [])
    )
    result: list[str] = []
    for phrase in ordered:
        if phrase not in result and any(normalize_match_text(phrase) in text for text in haystacks):
            result.append(phrase)
    return result


def validate_discovery_page(
    payload: dict[str, Any],
    repository: str,
    *,
    expected_total: int | None,
    seen_cursors: set[str],
) -> dict[str, Any]:
    if payload.get("errors"):
        raise GateError("graphql_errors")
    repo = payload.get("data", {}).get("repository")
    if not isinstance(repo, dict) or repo.get("nameWithOwner") != repository:
        raise GateError("repository_identity")
    connection = repo.get("issues")
    if not isinstance(connection, dict):
        raise GateError("issues_connection")
    total = connection.get("totalCount")
    if not isinstance(total, int) or (expected_total is not None and total != expected_total):
        raise GateError("total_count_drift")
    page_info = connection.get("pageInfo", {})
    has_next = page_info.get("hasNextPage")
    cursor = page_info.get("endCursor")
    if has_next:
        if not isinstance(cursor, str) or not cursor:
            raise GateError("cursor_missing")
        if cursor in seen_cursors:
            raise GateError("cursor_repeat")
    for node in connection.get("nodes", []):
        if node.get("__typename") != "Issue" or node.get("state") != "CLOSED":
            raise GateError("issue_identity")
        if node.get("labels", {}).get("pageInfo", {}).get("hasNextPage"):
            raise GateError("incomplete_labels")
        expected_prefix = f"https://github.com/{repository}/issues/"
        if not str(node.get("url", "")).startswith(expected_prefix):
            raise GateError("issue_url")
    return {"total_count": total, "next_cursor": cursor if has_next else None, "terminal": not has_next}


def _connection_state(
    connection: dict[str, Any],
    *,
    label: str,
    expected_total: int | None,
    seen_cursors: set[str],
) -> tuple[int, str | None, bool, str | None]:
    total = connection.get("totalCount")
    if not isinstance(total, int) or (expected_total is not None and total != expected_total):
        raise GateError(f"{label}_total_count_drift")
    page = connection.get("pageInfo", {})
    has_next = page.get("hasNextPage")
    cursor = page.get("endCursor")
    if has_next:
        if not isinstance(cursor, str) or not cursor:
            raise GateError(f"{label}_cursor_missing")
        if cursor in seen_cursors:
            raise GateError(f"{label}_cursor_repeat")
    return total, cursor if has_next else None, not bool(has_next), cursor


def validate_issue_evidence_page(
    payload: dict[str, Any],
    *,
    repository: str,
    issue_number: int,
    expected_comment_total: int | None,
    expected_timeline_total: int | None,
    seen_comment_cursors: set[str],
    seen_timeline_cursors: set[str],
) -> dict[str, Any]:
    if payload.get("errors"):
        raise GateError("graphql_errors")
    issue_node = payload.get("data", {}).get("repository", {}).get("issue")
    if not isinstance(issue_node, dict):
        raise GateError("null_issue")
    if issue_node.get("__typename") != "Issue" or issue_node.get("number") != issue_number:
        raise GateError("issue_identity")
    if issue_node.get("state") != "CLOSED" or not issue_node.get("closedAt"):
        raise GateError("issue_state")
    expected_url = f"https://github.com/{repository}/issues/{issue_number}"
    if issue_node.get("url") != expected_url:
        raise GateError("issue_url")
    if issue_node.get("labels", {}).get("pageInfo", {}).get("hasNextPage"):
        raise GateError("incomplete_labels")
    comment_total, comments_after, comments_terminal, comments_cursor = _connection_state(
        issue_node.get("comments", {}),
        label="comments",
        expected_total=expected_comment_total,
        seen_cursors=seen_comment_cursors,
    )
    timeline_total, timeline_after, timeline_terminal, timeline_cursor = _connection_state(
        issue_node.get("timelineItems", {}),
        label="timeline",
        expected_total=expected_timeline_total,
        seen_cursors=seen_timeline_cursors,
    )
    return {
        "comment_total": comment_total,
        "timeline_total": timeline_total,
        "comments_after": comments_after,
        "timeline_after": timeline_after,
        "comments_cursor": comments_cursor,
        "timeline_cursor": timeline_cursor,
        "comments_terminal": comments_terminal,
        "timeline_terminal": timeline_terminal,
        "terminal": comments_terminal and timeline_terminal,
    }


def validate_fix_evidence(
    payload: dict[str, Any], repository: str, expected_oid: str
) -> dict[str, Any] | None:
    if payload.get("errors"):
        raise GateError("graphql_errors")
    repository_node = payload.get("data", {}).get("repository")
    if not isinstance(repository_node, dict):
        raise GateError("fix_identity")
    node = repository_node.get("object")
    if node is None or isinstance(node, dict) and node.get("__typename") != "Commit":
        return None
    if not isinstance(node, dict):
        raise GateError("fix_identity")
    if node.get("oid") != expected_oid or node.get("repository", {}).get("nameWithOwner") != repository:
        raise GateError("fix_identity")
    if node.get("url") != f"https://github.com/{repository}/commit/{expected_oid}":
        raise GateError("fix_url")
    parents = node.get("parents", {})
    if parents.get("pageInfo", {}).get("hasNextPage"):
        raise GateError("incomplete_parents")
    parent_ids = [item.get("oid") for item in parents.get("nodes", [])]
    if not parent_ids or any(not isinstance(value, str) or len(value) != 40 for value in parent_ids):
        raise GateError("fix_parents")
    return {"oid": expected_oid, "repository": repository, "parents": parent_ids, "url": node["url"]}


def unique_admissible_fix(
    valid_fix_records: dict[str, dict[str, Any]], used_fix_shas: set[str]
) -> str | None:
    eligible = [sha for sha in valid_fix_records if sha not in used_fix_shas]
    return eligible[0] if len(eligible) == 1 else None


def extract_fix_candidates(timeline_nodes: Sequence[dict[str, Any]]) -> list[str]:
    candidates: list[str] = []
    for item in timeline_nodes:
        typename = item.get("__typename")
        subject = None
        if typename == "ClosedEvent":
            subject = item.get("closer")
        elif typename == "CrossReferencedEvent":
            subject = item.get("source")
        elif typename == "ConnectedEvent":
            subject = item.get("subject")
        if not isinstance(subject, dict) or subject.get("__typename") != "PullRequest":
            continue
        oid = subject.get("mergeCommit", {}).get("oid")
        if isinstance(oid, str) and len(oid) == 40 and oid not in candidates:
            candidates.append(oid)
    return candidates


def capture_issue_evidence(
    *,
    request: Callable[[str, dict[str, Any], str], bytes],
    repository: str,
    neutral_id: str,
    issue_number: int,
    payload_root: Path,
    query_sha256: str,
) -> dict[str, Any]:
    owner, name = _owner_name(repository)
    comments_after: str | None = None
    timeline_after: str | None = None
    comments_terminal = False
    timeline_terminal = False
    seen_comment_cursors: set[str] = set()
    seen_timeline_cursors: set[str] = set()
    expected_comment_total: int | None = None
    expected_timeline_total: int | None = None
    comment_nodes: dict[str, dict[str, Any]] = {}
    timeline_nodes: list[dict[str, Any]] = []
    page_manifest: list[dict[str, Any]] = []
    page_hashes: list[str] = []
    issue_identity: dict[str, Any] | None = None
    page_index = 0
    while True:
        variables = {
            "owner": owner,
            "name": name,
            "number": issue_number,
            "commentsAfter": comments_after,
            "timelineAfter": timeline_after,
        }
        key = f"issue:{neutral_id}:{page_index}"
        raw = request("issue_evidence", variables, key)
        relative = f"issue_pages/{neutral_id}/issue_page_{page_index:04d}.json"
        path = Path(payload_root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"issue_json: {exc}") from exc
        state = validate_issue_evidence_page(
            payload,
            repository=repository,
            issue_number=issue_number,
            expected_comment_total=expected_comment_total,
            expected_timeline_total=expected_timeline_total,
            seen_comment_cursors=seen_comment_cursors,
            seen_timeline_cursors=seen_timeline_cursors,
        )
        if expected_comment_total is None:
            expected_comment_total = state["comment_total"]
            expected_timeline_total = state["timeline_total"]
        node = payload["data"]["repository"]["issue"]
        identity = {key: node.get(key) for key in (
            "__typename", "id", "number", "url", "state", "title", "bodyText",
            "createdAt", "updatedAt", "closedAt", "labels",
        )}
        if issue_identity is None:
            issue_identity = identity
        elif identity != issue_identity:
            raise GateError("issue_identity_drift")
        comment_page = node["comments"].get("nodes", [])
        timeline_page = node["timelineItems"].get("nodes", [])
        if comments_terminal and comment_page:
            raise GateError("comments_after_terminal")
        if timeline_terminal and timeline_page:
            raise GateError("timeline_after_terminal")
        for comment in comment_page:
            comment_id = comment.get("id")
            if not isinstance(comment_id, str) or not comment_id:
                raise GateError("comment_identity")
            prior = comment_nodes.get(comment_id)
            if prior is not None and prior != comment:
                raise GateError("comment_identity_drift")
            comment_nodes[comment_id] = comment
        for item in timeline_page:
            if item not in timeline_nodes:
                timeline_nodes.append(item)
        response_sha = _sha256(raw)
        page_hashes.append(response_sha)
        page_manifest.append({
            "kind": "issue",
            "neutral_id": neutral_id,
            "page_index": page_index,
            "request_key": key,
            "variables": variables,
            "query_sha256": query_sha256,
            "response_sha256": response_sha,
            "path": relative,
        })
        next_comments = state["comments_after"]
        next_timeline = state["timeline_after"]
        if not comments_terminal and next_comments is not None:
            seen_comment_cursors.add(next_comments)
            comments_after = next_comments
        elif not comments_terminal and state["comments_terminal"]:
            comments_terminal = True
            comments_after = state["comments_cursor"]
        if not timeline_terminal and next_timeline is not None:
            seen_timeline_cursors.add(next_timeline)
            timeline_after = next_timeline
        elif not timeline_terminal and state["timeline_terminal"]:
            timeline_terminal = True
            timeline_after = state["timeline_cursor"]
        page_index += 1
        if state["terminal"]:
            break
    if len(comment_nodes) != expected_comment_total:
        raise GateError("comments_incomplete")
    if len(timeline_nodes) != expected_timeline_total:
        raise GateError("timeline_incomplete")
    return {
        "issue": issue_identity,
        "comments": list(comment_nodes.values()),
        "timeline": timeline_nodes,
        "fix_candidates": extract_fix_candidates(timeline_nodes),
        "page_manifest": page_manifest,
        "page_sha256s": page_hashes,
        "pages_sha256": _sha256(json.dumps(page_hashes, separators=(",", ":")).encode("utf-8")),
    }


def build_review_queue(
    records: Sequence[dict[str, Any]],
    scope: dict[str, Any],
    collision_universe: dict[str, Any],
) -> list[dict[str, Any]]:
    repository_specs = {item["repository"]: item for item in scope["repositories"]}
    counters = {repo: int(spec["id_start"]) for repo, spec in repository_specs.items()}
    collision_urls = set(collision_universe.get("issue_urls", set()))
    collision_node_ids = set(collision_universe.get("issue_node_ids", set()))
    collision_repo_numbers = {
        (url.removeprefix("https://github.com/").rsplit("/issues/", 1)[0], int(url.rsplit("/", 1)[1]))
        for url in collision_urls
        if "/issues/" in url and url.rsplit("/", 1)[1].isdigit()
    }
    seen_repo_number: set[tuple[str, int]] = set()
    seen_node_ids: set[str] = set()
    seen_urls: set[str] = set()
    result: list[dict[str, Any]] = []
    for record in records:
        repo = record["repository"]
        key = (repo, int(record["number"]))
        node_id = str(record.get("id", ""))
        url = str(record.get("url", ""))
        if key in seen_repo_number or node_id in seen_node_ids or url in seen_urls:
            raise GateError("duplicate_issue")
        seen_repo_number.add(key)
        seen_node_ids.add(node_id)
        seen_urls.add(url)
        collision = key in collision_repo_numbers or node_id in collision_node_ids or url in collision_urls
        row = dict(record)
        row["collision"] = collision
        if collision:
            row["neutral_id"] = ""
        else:
            spec = repository_specs[repo]
            row["neutral_id"] = f'{spec["id_prefix"]}{counters[repo]:02d}'
            counters[repo] += 1
        result.append(row)
    return result


def apply_repository_stops(
    rows: Sequence[dict[str, Any]], quotas: dict[str, int]
) -> list[dict[str, Any]]:
    counts = {repo: 0 for repo in quotas}
    output: list[dict[str, Any]] = []
    for original in rows:
        row = dict(original)
        repo = row["repository"]
        if counts[repo] >= quotas[repo]:
            row["counted"] = False
            row["status"] = "NOT_REVIEWED_AFTER_STOP"
        elif row.get("decision") == "ADMIT_PENDING_REPRO":
            counts[repo] += 1
            row["counted"] = True
            row["status"] = "REVIEWED"
        else:
            row["counted"] = False
            row["status"] = "REVIEWED"
        output.append(row)
    return output


class GraphQLCommandRunner:
    def __init__(self, *, executor: Callable[[Sequence[str]], tuple[int, bytes, bytes]]) -> None:
        self.executor = executor
        self.evidence_request_count = 0
        self._keys: set[str] = set()
        self.terminal = False

    def request(self, query: str, variables: dict[str, Any], *, request_key: str) -> bytes:
        if self.terminal:
            raise GateError("runner_terminal")
        if request_key in self._keys:
            self.terminal = True
            raise GateError("duplicate_request")
        self._keys.add(request_key)
        self.evidence_request_count += 1
        argv = graphql_argv(query, variables)
        exit_code, stdout, stderr = self.executor(argv)
        if exit_code != 0:
            self.terminal = True
            raise GateError(f"graphql_command_failed: {stderr.decode('utf-8', errors='replace')}")
        return stdout


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    execute_parser = commands.add_parser("execute")
    execute_parser.add_argument("--root", type=Path, required=True)
    execute_parser.add_argument("--candidate-root", type=Path, required=True)
    execute_parser.add_argument("--authority", required=True)
    execute_parser.add_argument("--journal", type=Path, required=True)
    return parser


def _canonical_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n")


def graphql_argv(query: str, variables: dict[str, Any]) -> list[str]:
    argv = ["gh", "api", "graphql", "-f", f"query={query}"]
    key_order = ("owner", "name", "number", "after", "commentsAfter", "timelineAfter", "oid")
    if any(key not in key_order for key in variables):
        raise GateError("graphql_variable_key")
    for key in key_order:
        if key not in variables:
            continue
        value = variables[key]
        if value is None:
            continue
        flag = "-F" if isinstance(value, int) and not isinstance(value, bool) else "-f"
        argv.extend([flag, f"{key}={value}"])
    return argv


def make_journaled_request(frozen: dict[str, Any], runner: Any) -> Callable[[str, dict[str, Any], str], bytes]:
    def request(operation: str, variables: dict[str, Any], request_key: str) -> bytes:
        query = frozen["queries"][operation]["bytes"].decode("utf-8")
        argv = graphql_argv(query, variables)
        stdout, _ = runner.run(
            argv,
            evidence_request=True,
            request_key=request_key,
        )
        return stdout

    return request


DECISION_INPUT_KEYS = {
    "neutral_id",
    "fixed_sha",
    "crit_real_public_fix",
    "crit_in_numerical_scope",
    "crit_dual_arm_repro",
    "decision",
    "decision_reason",
    "exclusion_class",
    "mechanism",
    "analysis_id",
    "alias",
}


def validate_decision_input(decision: dict[str, Any]) -> None:
    if set(decision) != DECISION_INPUT_KEYS:
        raise GateError("decision_schema")
    if not all(isinstance(decision[key], str) for key in DECISION_INPUT_KEYS):
        raise GateError("decision_schema")
    admitted = (
        decision["crit_real_public_fix"] == "PASS"
        and decision["crit_in_numerical_scope"] == "PASS"
    )
    if (decision["decision"] == "ADMIT_PENDING_REPRO") != admitted:
        raise GateError("decision_biconditional")
    if decision["crit_dual_arm_repro"] != "PENDING":
        raise GateError("a2_not_pending")
    if decision["analysis_id"] or decision["alias"]:
        raise GateError("blind_fields")
    if not decision["decision_reason"] or not decision["mechanism"]:
        raise GateError("decision_schema")


def read_review_decision(*, envelope: dict[str, Any], input_stream: Any, output_stream: Any) -> dict[str, Any]:
    output_stream.write(json.dumps(
        {"review_envelope": envelope}, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ) + "\n")
    output_stream.flush()
    try:
        raw = input_stream.readline() if hasattr(input_stream, "readline") else next(input_stream)
        decision = json.loads(raw)
    except (StopIteration, EOFError, json.JSONDecodeError) as exc:
        raise GateError("decision_stream") from exc
    if not isinstance(decision, dict):
        raise GateError("decision_schema")
    validate_decision_input(decision)
    return decision


def _owner_name(repository: str) -> tuple[str, str]:
    owner, name = repository.split("/", 1)
    return owner, name


def verify_environment_gate_before_collection(
    *, root: Path, journal: Path, runner: Any
) -> dict[str, str]:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            record = json.loads(line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"environment_journal_json: {exc}") from exc
        if line != _common.canonical_json_bytes(record) + b"\n":
            raise GateError("environment_journal_canonical")
        records.append(record)
    intents = [
        row
        for row in records
        if row.get("stage") == "operation_intent"
        and row.get("operation_name") == "verify_environment_seal"
    ]
    if len(intents) != 1 or not records:
        raise GateError("environment_verification_intent")
    intent = intents[0]
    completions = [
        row
        for row in records
        if row.get("stage") == "operation"
        and row.get("operation_key") == intent.get("operation_key")
    ]
    if (
        len(completions) != 1
        or records[-1] != completions[0]
        or records.index(completions[0]) != records.index(intent) + 1
    ):
        raise GateError("environment_verification_boundary")
    metadata = completions[0].get("metadata")
    seal_path = Path(root) / "data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json"
    if (
        not isinstance(metadata, dict)
        or metadata.get("evidence_request_count") != 0
        or metadata.get("seal_sha256")
        != hashlib.sha256(seal_path.read_bytes()).hexdigest()
        or not isinstance(metadata.get("seal_commit"), str)
        or len(metadata["seal_commit"]) != 40
        or runner.evidence_request_count != 0
    ):
        raise GateError("environment_verification_binding")
    root_text = str(Path(root))
    head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"
    ])
    if head_raw.decode("ascii").strip() != metadata["seal_commit"] or status_raw:
        raise GateError("environment_verification_drift")
    return {
        "seal_commit": metadata["seal_commit"],
        "seal_sha256": metadata["seal_sha256"],
    }


def execute(
    *,
    root: Path,
    candidate_root: Path,
    authority: str,
    journal: Path,
    request_fn: Callable[[str, dict[str, Any], str], bytes] | None = None,
    decisions: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if len(authority) != 40:
        raise GateError("authority")
    repository_root = Path(root)
    frozen_root = repository_root / "data/external_slice/supplemental_r3"
    frozen = load_frozen_contract(frozen_root)
    payload_root = Path(candidate_root) / "data/external_slice/supplemental_r3"
    if payload_root.exists():
        raise GateError("candidate_root_exists")
    shared_runner = None
    operation_key = None
    if request_fn is None:
        if not Path(journal).is_file() or Path(journal).is_symlink():
            raise GateError("journal_missing")
        shared_runner = _common.TerminalCommandRunner(Path(journal))
        environment_gate = verify_environment_gate_before_collection(
            root=repository_root, journal=Path(journal), runner=shared_runner
        )
        operation_key = shared_runner.begin_operation(
            "candidate_collection",
            {
                "candidate_root": str(Path(candidate_root)),
                "authority": authority,
                "environment_seal_commit": environment_gate["seal_commit"],
                "environment_seal_sha256": environment_gate["seal_sha256"],
            },
        )
        active_request = make_journaled_request(frozen, shared_runner)
    else:
        active_request = request_fn
    payload_root.mkdir(parents=True)
    decision_iter = iter(decisions) if decisions is not None else None
    request_count = 0
    request_keys: set[str] = set()
    page_manifest: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    def request(operation: str, variables: dict[str, Any], key: str) -> bytes:
        nonlocal request_count
        if key in request_keys:
            raise GateError("duplicate_request")
        request_keys.add(key)
        request_count += 1
        return active_request(operation, variables, key)

    for repo_spec in frozen["scope"]["repositories"]:
        repository = repo_spec["repository"]
        owner, name = _owner_name(repository)
        after = None
        seen_cursors: set[str] = set()
        expected_total = None
        page_index = 0
        terminal = False
        while not terminal:
            variables = {"owner": owner, "name": name, "after": after}
            key = f"discovery:{repository}:{page_index}"
            raw = request("discovery", variables, key)
            relative = f"transport_pages/{repo_spec['order']:02d}_{owner}_{name}_page_{page_index:04d}.json"
            path = payload_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            payload = json.loads(raw.decode("utf-8"))
            state = validate_discovery_page(
                payload,
                repository,
                expected_total=expected_total,
                seen_cursors=seen_cursors,
            )
            if expected_total is None:
                expected_total = state["total_count"]
            connection = payload["data"]["repository"]["issues"]
            for node in connection["nodes"]:
                phrases = matched_phrases(node, repository, frozen["scope"])
                if phrases and node.get("createdAt", "") <= frozen["scope"]["created_cutoff"]:
                    record = {
                        **node,
                        "repository": repository,
                        "repository_order": repo_spec["order"],
                        "matched_phrases": phrases,
                    }
                    record["record_id"] = f'{repository}#{node["number"]}'
                    record["record_sha256"] = _sha256(json.dumps(
                        record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                    ).encode("utf-8"))
                    records.append(record)
            page_manifest.append({
                "kind": "discovery", "repository": repository, "page_index": page_index,
                "request_key": key,
                "variables": variables, "query_sha256": frozen["queries"]["discovery"]["sha256"],
                "response_sha256": _sha256(raw), "path": relative,
            })
            after = state["next_cursor"]
            if after is not None:
                seen_cursors.add(after)
            terminal = state["terminal"]
            page_index += 1

    collision_payload = json.loads(
        (frozen_root / "COLLISION_UNIVERSE.json").read_text(encoding="utf-8")
    )
    collision_values = collision_payload.get("collision_sets", collision_payload)
    queue = build_review_queue(records, frozen["scope"], collision_values)
    decisions_out: list[dict[str, Any]] = []
    evidence_manifest: list[dict[str, Any]] = []
    quotas = frozen["quotas"]["quota_vector"]
    admitted = {repo: 0 for repo in quotas}
    used_fix_shas = set(collision_values.get("known_fix_shas", []))
    used_issue_fix_pairs: set[tuple[str, str]] = set()

    for row in queue:
        repository = row["repository"]
        if row["collision"] or admitted[repository] >= quotas[repository]:
            row["status"] = "COLLISION" if row["collision"] else "NOT_REVIEWED_AFTER_STOP"
            continue
        row["status"] = "REVIEWED"
        owner, name = _owner_name(repository)
        number = int(row["number"])
        issue_capture = capture_issue_evidence(
            request=request,
            repository=repository,
            neutral_id=row["neutral_id"],
            issue_number=number,
            payload_root=payload_root,
            query_sha256=frozen["queries"]["issue_evidence"]["sha256"],
        )
        candidates = issue_capture["fix_candidates"]
        page_manifest.extend(issue_capture["page_manifest"])
        fix_evidence: list[dict[str, Any]] = []
        valid_fix_records: dict[str, dict[str, Any]] = {}
        for fix_index, candidate_sha in enumerate(candidates):
            fix_variables = {"owner": owner, "name": name, "oid": candidate_sha}
            fix_key = f"fix:{row['neutral_id']}:{fix_index}"
            raw_fix = request("fix_evidence", fix_variables, fix_key)
            fix_relative = f"fix_pages/{row['neutral_id']}/fix_page_{fix_index:04d}.json"
            fix_path = payload_root / fix_relative
            fix_path.parent.mkdir(parents=True, exist_ok=True)
            fix_path.write_bytes(raw_fix)
            response_sha = _sha256(raw_fix)
            fix_manifest = {
                "kind": "fix",
                "neutral_id": row["neutral_id"],
                "page_index": fix_index,
                "request_key": fix_key,
                "variables": fix_variables,
                "query_sha256": frozen["queries"]["fix_evidence"]["sha256"],
                "response_sha256": response_sha,
                "path": fix_relative,
            }
            page_manifest.append(fix_manifest)
            try:
                raw_payload = json.loads(raw_fix.decode("utf-8"))
            except Exception as exc:
                raise GateError(f"fix_json: {exc}") from exc
            fix_record = validate_fix_evidence(raw_payload, repository, candidate_sha)
            if fix_record is None:
                fix_evidence.append({
                    "fixed_sha": candidate_sha,
                    "status": "INVALID_PUBLIC_FIX_EVIDENCE",
                    "reason": "fix_not_commit",
                    "response_sha256": response_sha,
                    "path": fix_relative,
                })
            else:
                valid_fix_records[candidate_sha] = fix_record
                fix_evidence.append({
                    "fixed_sha": candidate_sha,
                    "status": "VALID_PUBLIC_FIX_EVIDENCE",
                    "record": fix_record,
                    "response_sha256": response_sha,
                    "path": fix_relative,
                })
        if decision_iter is None:
            decision = read_review_decision(
                envelope={
                    "neutral_id": row["neutral_id"],
                    "repository": repository,
                    "issue_number": number,
                    "issue_url": row["url"],
                    "fix_candidates": candidates,
                    "issue": issue_capture["issue"],
                    "comments": issue_capture["comments"],
                    "timeline": issue_capture["timeline"],
                    "fix_evidence": fix_evidence,
                    "issue_page_sha256s": issue_capture["page_sha256s"],
                    "issue_page_manifest": issue_capture["page_manifest"],
                },
                input_stream=sys.stdin,
                output_stream=sys.stdout,
            )
        else:
            try:
                decision = next(decision_iter)
            except StopIteration as exc:
                raise GateError("decision_stream") from exc
        validate_decision_input(decision)
        if decision.get("neutral_id") != row["neutral_id"]:
            raise GateError("decision_order")
        is_admit = decision.get("crit_real_public_fix") == "PASS" and decision.get("crit_in_numerical_scope") == "PASS"
        if (decision.get("decision") == "ADMIT_PENDING_REPRO") != is_admit:
            raise GateError("decision_biconditional")
        if decision.get("crit_dual_arm_repro") != "PENDING" or decision.get("analysis_id") != "" or decision.get("alias") != "":
            raise GateError("blind_fields")
        fixed_sha = decision.get("fixed_sha", "")
        fix_record = None
        unique_fix = unique_admissible_fix(valid_fix_records, used_fix_shas)
        if is_admit:
            if unique_fix is None or fixed_sha != unique_fix:
                raise GateError("ambiguous_or_missing_public_fix")
            issue_fix = (row["url"], fixed_sha)
            if fixed_sha in used_fix_shas or issue_fix in used_issue_fix_pairs:
                raise GateError("fix_collision")
            fix_record = valid_fix_records[fixed_sha]
            used_fix_shas.add(fixed_sha)
            used_issue_fix_pairs.add(issue_fix)
            admitted[repository] += 1
        elif unique_fix is None and fixed_sha:
            raise GateError("excluded_fixed_sha")
        combined = {
            **row,
            **decision,
            "issue_url": row["url"],
            "issue_page_sha256": issue_capture["pages_sha256"],
            "issue_page_sha256s": issue_capture["page_sha256s"],
            "fix_record": fix_record,
            "fix_evidence": fix_evidence,
        }
        decisions_out.append(combined)
        evidence_relative = f"admission_evidence/{row['neutral_id']}/evidence.json"
        evidence_path = payload_root / evidence_relative
        _canonical_write(evidence_path, combined)
        evidence_manifest.append({"neutral_id": row["neutral_id"], "path": evidence_relative, "sha256": _sha256(evidence_path.read_bytes())})

    if admitted != quotas:
        raise GateError(f"DISTRIBUTION_TARGET_AT_RISK: {admitted!r}")
    if decision_iter is not None:
        try:
            next(decision_iter)
        except StopIteration:
            pass
        else:
            raise GateError("decision_stream_extra")
    snapshot = {"schema_version": 1, "authority": authority, "records": records, "page_manifest": page_manifest}
    _canonical_write(payload_root / "ISSUE_SNAPSHOT.json", snapshot)
    _canonical_write(payload_root / "REVIEW_QUEUE.json", {"schema_version": 1, "rows": queue})
    _canonical_write(payload_root / "REVIEW_DECISIONS.json", {"schema_version": 1, "rows": decisions_out})
    _canonical_write(payload_root / "EVIDENCE_SNAPSHOT.json", {"schema_version": 1, "artifacts": evidence_manifest})
    _canonical_write(payload_root / "PAGE_MANIFESTS.json", {"schema_version": 1, "pages": page_manifest})
    sheet_path = payload_root / "admission_sheet.cursor_candidate.csv"
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "neutral_id", "repository", "issue_url", "fixed_sha",
        "crit_real_public_fix", "crit_dual_arm_repro", "crit_in_numerical_scope",
        "decision", "analysis_id", "alias", "record_id", "record_sha256",
    ]
    with sheet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        for row in decisions_out:
            writer.writerow({key: row.get(key, "") for key in header})
    if shared_runner is not None and operation_key is not None:
        shared_runner.complete_operation(
            operation_key,
            {"quota_results": admitted, "evidence_request_count": request_count},
        )
    return {"quota_results": admitted, "evidence_request_count": request_count, "candidate_root": str(payload_root), "journal": str(journal)}


def main(
    argv: Sequence[str] | None = None,
    *,
    execute_fn: Callable[..., int] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    handler = execute_fn or execute
    try:
        result = handler(
            root=args.root,
            candidate_root=args.candidate_root,
            authority=args.authority,
            journal=args.journal,
        )
    except Exception as exc:
        if execute_fn is None and Path(args.journal).is_file():
            _common.persist_cli_failure(args.journal, "mine_execute", exc)
        raise
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
