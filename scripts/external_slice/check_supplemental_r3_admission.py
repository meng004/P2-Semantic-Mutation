#!/usr/bin/env python3
"""Independent Supplemental R3 admission and publication checks."""

from __future__ import annotations

import argparse
import ctypes
import csv
import errno
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Callable, Sequence


class GateError(RuntimeError):
    pass


EXPECTED_QUOTAS = {
    "cornellius-gp/gpytorch": 2,
    "jonathf/chaospy": 3,
    "SALib/SALib": 3,
}
PAYLOAD_REL = Path("data/external_slice/supplemental_r3")
REQUIRED_PAYLOAD_FILES = {
    "ISSUE_SNAPSHOT.json",
    "REVIEW_QUEUE.json",
    "REVIEW_DECISIONS.json",
    "admission_sheet.cursor_candidate.csv",
    "EVIDENCE_SNAPSHOT.json",
    "PAGE_MANIFESTS.json",
}
PAYLOAD_MANIFEST = "PAYLOAD_MANIFEST_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"
OPTIONAL_PAYLOAD_FILES = {PAYLOAD_MANIFEST}
VM_SEAL_REL = Path("data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json")
EVIDENCE_BRANCH = "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence"
PAYLOAD_COMMIT_COMMAND = (
    "git", "commit", "-m", "evidence(external): publish Supplemental R3 payload"
)
HANDOFF_COMMIT_COMMAND = (
    "git", "commit", "-m", "evidence(external): add Supplemental R3 handoff"
)
PUSH_COMMAND = ("git", "push", "-u", "origin", EVIDENCE_BRANCH)
ENVIRONMENT_SEAL_COMMIT_COMMAND = (
    "git", "commit", "-m", "evidence(external): seal Supplemental R3 environment"
)
BUNDLE_RED_PATHS = (
    "tests/external_slice/test_supplemental_r3_ref_isolation.py",
    "tests/external_slice/test_mine_supplemental_r3.py",
    "tests/external_slice/test_check_supplemental_r3_admission.py",
    "tests/external_slice/test_check_supplemental_r3_handoff_hashes.py",
    "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
    "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
)
BUNDLE_GREEN_PATHS = (
    "scripts/external_slice/supplemental_r3_common.py",
    "scripts/external_slice/supplemental_r3_bootstrap.py",
    "scripts/external_slice/mine_supplemental_r3.py",
    "scripts/external_slice/check_supplemental_r3_admission.py",
    "scripts/external_slice/check_supplemental_r3_handoff_hashes.py",
)
BUNDLE_SEAL_PATHS = (
    "data/external_slice/supplemental_r3/LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
    "data/external_slice/supplemental_r3/LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
    "data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
)
CANDIDATE_SHEET_FIELDS = [
    "neutral_id", "repository", "issue_url", "fixed_sha",
    "crit_real_public_fix", "crit_dual_arm_repro", "crit_in_numerical_scope",
    "decision", "analysis_id", "alias", "record_id", "record_sha256",
]


def _load_common():
    path = Path(__file__).with_name("supplemental_r3_common.py")
    spec = importlib.util.spec_from_file_location("_supplemental_r3_common_admission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load supplemental_r3_common")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_common = _load_common()


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"{label}_json: {exc}") from exc


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFC", value or "").casefold()


def _extract_fix_candidates(timeline_rows: Sequence[dict[str, Any]]) -> list[str]:
    candidates: list[str] = []
    for item in timeline_rows:
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


def _classify_fix_evidence(
    *, payload: dict[str, Any], repository: str, expected_oid: str, path: str, response_sha256: str
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if payload.get("errors"):
        raise GateError("graphql_errors")
    repository_node = payload.get("data", {}).get("repository")
    if not isinstance(repository_node, dict):
        raise GateError("fix_identity")
    node = repository_node.get("object")
    if node is None or isinstance(node, dict) and node.get("__typename") != "Commit":
        return ({
            "fixed_sha": expected_oid,
            "status": "INVALID_PUBLIC_FIX_EVIDENCE",
            "reason": "fix_not_commit",
            "response_sha256": response_sha256,
            "path": path,
        }, None)
    if not isinstance(node, dict):
        raise GateError("fix_identity")
    if node.get("oid") != expected_oid or node.get("repository", {}).get("nameWithOwner") != repository:
        raise GateError("fix_identity")
    if node.get("url") != f"https://github.com/{repository}/commit/{expected_oid}":
        raise GateError("fix_url")
    parents = node.get("parents", {})
    parent_ids = [item.get("oid") for item in parents.get("nodes", [])]
    if parents.get("pageInfo", {}).get("hasNextPage"):
        raise GateError("incomplete_parents")
    if not parent_ids or any(not isinstance(value, str) or len(value) != 40 for value in parent_ids):
        raise GateError("fix_parents")
    record = {
        "oid": expected_oid,
        "repository": repository,
        "parents": [item.get("oid") for item in node["parents"]["nodes"]],
        "url": node["url"],
    }
    return ({
        "fixed_sha": expected_oid,
        "status": "VALID_PUBLIC_FIX_EVIDENCE",
        "record": record,
        "response_sha256": response_sha256,
        "path": path,
    }, record)


def verify_review_stop_closure(
    queue: Sequence[dict[str, Any]],
    decisions: Sequence[dict[str, Any]],
    quotas: dict[str, int],
    *,
    known_fix_shas: set[str],
) -> None:
    counts = {repository: 0 for repository in quotas}
    decision_index = 0
    for row in queue:
        repository = row.get("repository")
        if repository not in quotas:
            raise GateError("queue_repository")
        if row.get("collision") is True:
            if row.get("status") != "COLLISION" or row.get("neutral_id"):
                raise GateError("collision_status")
            continue
        if counts[repository] >= quotas[repository]:
            if row.get("status") != "NOT_REVIEWED_AFTER_STOP":
                raise GateError("stop_status")
            if any(item.get("neutral_id") == row.get("neutral_id") for item in decisions):
                raise GateError("decision_after_stop")
            continue
        if row.get("status") != "REVIEWED" or decision_index >= len(decisions):
            raise GateError("decision_prefix")
        decision = decisions[decision_index]
        if (
            decision.get("neutral_id") != row.get("neutral_id")
            or decision.get("repository") != repository
        ):
            raise GateError("decision_prefix")
        if decision.get("decision") == "ADMIT_PENDING_REPRO":
            fixed_sha = decision.get("fixed_sha")
            if fixed_sha in known_fix_shas:
                raise GateError("known_fix_reuse")
            counts[repository] += 1
        decision_index += 1
    if decision_index != len(decisions):
        raise GateError("decision_after_stop")
    if counts != quotas:
        raise GateError("quota_stop_closure")


def _independent_discovery_records(
    *, root: Path, pages: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    scope = _load_json(Path(root) / "SCOPE.json", "scope")
    transport = _load_json(Path(root) / "TRANSPORT_CONTRACT.json", "transport")
    query_record = transport.get("query_files", {}).get("discovery", {})
    query_path = Path(root).parents[2] / query_record.get("path", "")
    if not query_path.is_file() or hashlib.sha256(query_path.read_bytes()).hexdigest() != query_record.get("sha256"):
        raise GateError("discovery_query_binding")
    specs = {entry["repository"]: entry for entry in scope["repositories"]}
    expected_after = {repo: None for repo in specs}
    expected_total: dict[str, int] = {}
    records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, int]] = set()
    discovery_pages = [page for page in pages if page.get("kind") == "discovery"]
    orders = [specs.get(page.get("repository"), {}).get("order") for page in discovery_pages]
    if any(order is None for order in orders) or orders != sorted(orders):
        raise GateError("discovery_repository_order")
    for page in discovery_pages:
        repository = page.get("repository")
        if repository not in specs or page.get("query_sha256") != query_record.get("sha256"):
            raise GateError("discovery_manifest_binding")
        variables = page.get("variables", {})
        owner, name = repository.split("/", 1)
        if variables != {"owner": owner, "name": name, "after": expected_after[repository]}:
            raise GateError("discovery_cursor_binding")
        if "_payload_root" not in page:
            raise GateError("discovery_payload_root")
        payload = _load_json(Path(page["_payload_root"]) / page["path"], "raw_discovery")
        repo_node = payload.get("data", {}).get("repository", {})
        connection = repo_node.get("issues", {})
        if repo_node.get("nameWithOwner") != repository or not isinstance(connection.get("totalCount"), int):
            raise GateError("discovery_identity")
        total = connection["totalCount"]
        if repository in expected_total and expected_total[repository] != total:
            raise GateError("discovery_total_count")
        expected_total[repository] = total
        page_info = connection.get("pageInfo", {})
        next_after = page_info.get("endCursor") if page_info.get("hasNextPage") else None
        if page_info.get("hasNextPage") and not next_after:
            raise GateError("discovery_cursor")
        expected_after[repository] = next_after
        for node in connection.get("nodes", []):
            if node.get("__typename") != "Issue" or node.get("state") != "CLOSED":
                raise GateError("discovery_issue")
            if node.get("labels", {}).get("pageInfo", {}).get("hasNextPage"):
                raise GateError("discovery_labels")
            if node.get("url") != f'https://github.com/{repository}/issues/{node.get("number")}':
                raise GateError("discovery_issue_url")
            surfaces = [node.get("title", ""), node.get("bodyText", ""), "\n".join(
                str(label.get("name", "")) for label in node.get("labels", {}).get("nodes", [])
            )]
            phrases = []
            for phrase in list(scope["common_phrases"]) + list(scope["repository_phrases"][repository]):
                if phrase not in phrases and any(_normalize(phrase) in _normalize(surface) for surface in surfaces):
                    phrases.append(phrase)
            if phrases and node.get("createdAt", "") <= scope["created_cutoff"]:
                key = (repository, int(node["number"]))
                if key in seen_keys:
                    raise GateError("discovery_duplicate")
                seen_keys.add(key)
                record = {**node, "repository": repository, "repository_order": specs[repository]["order"], "matched_phrases": phrases}
                record["record_id"] = f'{repository}#{node["number"]}'
                record["record_sha256"] = hashlib.sha256(_canonical_bytes(record)).hexdigest()
                records.append(record)
    if any(value is not None for value in expected_after.values()):
        raise GateError("discovery_incomplete")
    return records


def reconstruct_from_raw(payload_root: Path, *, frozen_root: Path | None = None) -> dict[str, Any]:
    root = Path(payload_root)
    snapshot = _load_json(root / "ISSUE_SNAPSHOT.json", "issue_snapshot")
    queue_payload = _load_json(root / "REVIEW_QUEUE.json", "review_queue")
    decisions_payload = _load_json(root / "REVIEW_DECISIONS.json", "review_decisions")
    evidence_payload = _load_json(root / "EVIDENCE_SNAPSHOT.json", "evidence_snapshot")
    pages_payload = _load_json(root / "PAGE_MANIFESTS.json", "page_manifests")
    records = snapshot.get("records")
    queue = queue_payload.get("rows")
    decisions = decisions_payload.get("rows")
    artifacts = evidence_payload.get("artifacts")
    pages = pages_payload.get("pages")
    if not all(isinstance(value, list) for value in (records, queue, decisions, artifacts, pages)):
        raise GateError("replay_shape")
    if snapshot.get("page_manifest") != pages:
        raise GateError("page_manifest_binding")
    query_bindings: dict[str, str] = {}
    known_fix_shas: set[str] = set()
    if frozen_root is not None:
        transport = _load_json(Path(frozen_root) / "TRANSPORT_CONTRACT.json", "transport")
        for operation in ("discovery", "issue_evidence", "fix_evidence"):
            record = transport.get("query_files", {}).get(operation, {})
            query_path = Path(frozen_root).parents[2] / str(record.get("path", ""))
            if (
                not query_path.is_file()
                or query_path.is_symlink()
                or hashlib.sha256(query_path.read_bytes()).hexdigest() != record.get("sha256")
            ):
                raise GateError(f"query_binding: {operation}")
            query_bindings[operation] = record["sha256"]
    for page in pages:
        page["_payload_root"] = str(root)
    page_paths: set[str] = set()
    for page in pages:
        if not isinstance(page, dict):
            raise GateError("page_manifest_row")
        kind = page.get("kind")
        if kind not in {"discovery", "issue", "fix"}:
            raise GateError("page_manifest_kind")
        operation = {"discovery": "discovery", "issue": "issue_evidence", "fix": "fix_evidence"}[kind]
        if query_bindings and page.get("query_sha256") != query_bindings[operation]:
            raise GateError("page_manifest_query")
        relative = page.get("path")
        if not isinstance(relative, str) or relative in page_paths or ".." in Path(relative).parts:
            raise GateError("page_manifest_path")
        page_paths.add(relative)
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise GateError("page_manifest_path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != page.get("response_sha256"):
            raise GateError("page_manifest_hash")
        _load_json(path, "raw_page")
    raw_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.json")
        if path.is_file()
        and not path.is_symlink()
        and path.relative_to(root).as_posix().startswith(
            ("transport_pages/", "issue_pages/", "fix_pages/")
        )
    }
    if page_paths != raw_paths:
        raise GateError("page_manifest_raw_closure")
    if frozen_root is not None:
        rebuilt = _independent_discovery_records(root=Path(frozen_root), pages=pages)
        if rebuilt != records:
            raise GateError("independent_snapshot_rebuild")
        scope = _load_json(Path(frozen_root) / "SCOPE.json", "scope")
        collision_payload = _load_json(Path(frozen_root) / "COLLISION_UNIVERSE.json", "collision")
        collision = collision_payload.get("collision_sets", collision_payload)
        collision_urls = set(collision.get("issue_urls", []))
        collision_ids = set(collision.get("issue_node_ids", []))
        known_fix_shas = set(collision.get("known_fix_shas", []))
        repo_numbers = {
            (url.removeprefix("https://github.com/").rsplit("/issues/", 1)[0], int(url.rsplit("/", 1)[1]))
            for url in collision_urls
            if "/issues/" in url and url.rsplit("/", 1)[1].isdigit()
        }
        specs = {entry["repository"]: entry for entry in scope["repositories"]}
        counters = {repo: int(spec["id_start"]) for repo, spec in specs.items()}
        if len(queue) != len(rebuilt):
            raise GateError("independent_queue_rebuild")
        for source, actual_queue in zip(rebuilt, queue):
            repo = source["repository"]
            is_collision = (
                source["url"] in collision_urls
                or source["id"] in collision_ids
                or (repo, int(source["number"])) in repo_numbers
            )
            neutral_id = "" if is_collision else f'{specs[repo]["id_prefix"]}{counters[repo]:02d}'
            if not is_collision:
                counters[repo] += 1
            if actual_queue.get("collision") is not is_collision or actual_queue.get("neutral_id") != neutral_id:
                raise GateError("independent_queue_rebuild")
    for page in pages:
        page.pop("_payload_root", None)
    record_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise GateError("snapshot_record")
        record_id = record.get("record_id")
        record_hash = record.get("record_sha256")
        unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
        if (
            not isinstance(record_id, str)
            or record_id in record_by_id
            or hashlib.sha256(_canonical_bytes(unsigned)).hexdigest() != record_hash
        ):
            raise GateError("snapshot_record_binding")
        record_by_id[record_id] = record
    queue_by_id: dict[str, dict[str, Any]] = {}
    for row in queue:
        if not isinstance(row, dict) or row.get("record_id") not in record_by_id:
            raise GateError("queue_snapshot_binding")
        source = record_by_id[row["record_id"]]
        if any(row.get(key) != value for key, value in source.items()):
            raise GateError("queue_snapshot_binding")
        neutral_id = row.get("neutral_id")
        if neutral_id:
            if neutral_id in queue_by_id:
                raise GateError("neutral_id_duplicate")
            queue_by_id[neutral_id] = row
    verify_review_stop_closure(
        queue, decisions, EXPECTED_QUOTAS, known_fix_shas=known_fix_shas
    )
    verify_decision_uniqueness(decisions)
    decisions_by_id: dict[str, dict[str, Any]] = {}
    quotas = {repo: 0 for repo in EXPECTED_QUOTAS}
    used_fix_shas = set(known_fix_shas)
    for decision in decisions:
        if not isinstance(decision, dict) or decision.get("neutral_id") not in queue_by_id:
            raise GateError("decision_queue_binding")
        if decision["neutral_id"] in decisions_by_id:
            raise GateError("decision_duplicate")
        source = queue_by_id[decision["neutral_id"]]
        if any(decision.get(key) != value for key, value in source.items()):
            raise GateError("decision_queue_binding")
        validate_decision(decision)
        issue_pages = [
            page for page in pages
            if page.get("kind") == "issue" and page.get("neutral_id") == decision["neutral_id"]
        ]
        if not issue_pages:
            raise GateError("issue_evidence_missing")
        issue_pages.sort(key=lambda page: page.get("page_index", -1))
        if [page.get("page_index") for page in issue_pages] != list(range(len(issue_pages))):
            raise GateError("issue_page_sequence")
        comments_after = None
        timeline_after = None
        comments_terminal = False
        timeline_terminal = False
        comment_total = None
        timeline_total = None
        comment_ids: set[str] = set()
        timeline_rows: list[dict[str, Any]] = []
        owner, name = str(decision.get("repository", "")).split("/", 1)
        for page in issue_pages:
            if comments_terminal and timeline_terminal:
                raise GateError("issue_page_after_terminal")
            expected_variables = {
                "owner": owner,
                "name": name,
                "number": decision.get("number"),
                "commentsAfter": comments_after,
                "timelineAfter": timeline_after,
            }
            if page.get("variables") != expected_variables:
                raise GateError("issue_page_variables")
            raw_issue = _load_json(root / page["path"], "raw_issue")
            repository_node = raw_issue.get("data", {}).get("repository", {})
            issue = repository_node.get("issue", {})
            if (
                repository_node.get("nameWithOwner") != decision.get("repository")
                or issue.get("number") != decision.get("number")
                or issue.get("url") != decision.get("url")
                or issue.get("state") != "CLOSED"
            ):
                raise GateError("issue_evidence_binding")
            comments = issue.get("comments", {})
            timeline = issue.get("timelineItems", {})
            if comment_total is None:
                comment_total = comments.get("totalCount")
                timeline_total = timeline.get("totalCount")
                if not isinstance(comment_total, int) or not isinstance(timeline_total, int):
                    raise GateError("issue_total_count")
            elif comments.get("totalCount") != comment_total or timeline.get("totalCount") != timeline_total:
                raise GateError("issue_total_drift")
            comment_page = comments.get("nodes", [])
            timeline_page = timeline.get("nodes", [])
            if comments_terminal and comment_page:
                raise GateError("issue_comment_after_terminal")
            if timeline_terminal and timeline_page:
                raise GateError("issue_timeline_after_terminal")
            for comment in comment_page:
                comment_id = comment.get("id")
                if not isinstance(comment_id, str) or comment_id in comment_ids:
                    raise GateError("issue_comment_duplicate")
                comment_ids.add(comment_id)
            for item in timeline_page:
                if item not in timeline_rows:
                    timeline_rows.append(item)
            comments_info = comments.get("pageInfo", {})
            timeline_info = timeline.get("pageInfo", {})
            if not comments_terminal:
                if comments_info.get("hasNextPage"):
                    comments_after = comments_info.get("endCursor")
                    if not comments_after:
                        raise GateError("issue_comment_cursor")
                else:
                    comments_terminal = True
                    comments_after = comments_info.get("endCursor")
            elif comments_info.get("hasNextPage"):
                raise GateError("issue_comment_after_terminal")
            if not timeline_terminal:
                if timeline_info.get("hasNextPage"):
                    timeline_after = timeline_info.get("endCursor")
                    if not timeline_after:
                        raise GateError("issue_timeline_cursor")
                else:
                    timeline_terminal = True
                    timeline_after = timeline_info.get("endCursor")
            elif timeline_info.get("hasNextPage"):
                raise GateError("issue_timeline_after_terminal")
        if not comments_terminal or not timeline_terminal:
            raise GateError("issue_evidence_incomplete")
        if len(comment_ids) != comment_total or len(timeline_rows) != timeline_total:
            raise GateError("issue_evidence_incomplete")
        ordered_candidates = _extract_fix_candidates(timeline_rows)
        fix_pages = sorted(
            [
                page for page in pages
                if page.get("kind") == "fix" and page.get("neutral_id") == decision["neutral_id"]
            ],
            key=lambda page: page.get("page_index", -1),
        )
        if [page.get("page_index") for page in fix_pages] != list(range(len(ordered_candidates))):
            raise GateError("fix_page_sequence")
        rebuilt_fix_evidence: list[dict[str, Any]] = []
        valid_fix_records: dict[str, dict[str, Any]] = {}
        for page, candidate_sha in zip(fix_pages, ordered_candidates):
            if page.get("variables") != {"owner": owner, "name": name, "oid": candidate_sha}:
                raise GateError("fix_page_variables")
            raw_fix = _load_json(root / page["path"], "raw_fix")
            classification, record = _classify_fix_evidence(
                payload=raw_fix,
                repository=decision.get("repository"),
                expected_oid=candidate_sha,
                path=page["path"],
                response_sha256=page["response_sha256"],
            )
            rebuilt_fix_evidence.append(classification)
            if record is not None:
                valid_fix_records[candidate_sha] = record
        if decision.get("fix_evidence") != rebuilt_fix_evidence:
            raise GateError("fix_evidence_projection")
        eligible_fixes = [sha for sha in valid_fix_records if sha not in used_fix_shas]
        unique_fix = eligible_fixes[0] if len(eligible_fixes) == 1 else None
        decisions_by_id[decision["neutral_id"]] = decision
        if decision["decision"] == "ADMIT_PENDING_REPRO":
            repository = decision.get("repository")
            if repository not in quotas:
                raise GateError("decision_repository")
            if decision.get("fixed_sha") != unique_fix:
                raise GateError("ambiguous_or_missing_public_fix")
            if decision.get("fix_record") != valid_fix_records[decision["fixed_sha"]]:
                raise GateError("fix_record_projection")
            used_fix_shas.add(decision["fixed_sha"])
            quotas[repository] += 1
        elif unique_fix is None and decision.get("fixed_sha"):
            raise GateError("excluded_fixed_sha")
    verify_quota_results(quotas)
    decision_ids = set(decisions_by_id)
    issue_page_ids = {
        page.get("neutral_id") for page in pages if page.get("kind") == "issue"
    }
    fix_page_ids = {
        page.get("neutral_id") for page in pages if page.get("kind") == "fix"
    }
    if issue_page_ids != decision_ids or not fix_page_ids.issubset(decision_ids):
        raise GateError("evidence_page_after_stop")
    evidence_ids: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise GateError("evidence_artifact")
        neutral_id = artifact.get("neutral_id")
        relative = artifact.get("path")
        if neutral_id not in decisions_by_id or neutral_id in evidence_ids or not isinstance(relative, str):
            raise GateError("evidence_decision_binding")
        path = root / relative
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact.get("sha256"):
            raise GateError("evidence_hash")
        if _load_json(path, "admission_evidence") != decisions_by_id[neutral_id]:
            raise GateError("evidence_decision_binding")
        evidence_ids.add(neutral_id)
    if evidence_ids != set(decisions_by_id):
        raise GateError("evidence_decision_binding")
    verify_sheet_projection(root / "admission_sheet.cursor_candidate.csv", decisions)
    return {"quota_results": quotas, "page_count": len(pages), "decision_count": len(decisions)}


def verify_sheet_projection(path: Path, decisions: Sequence[dict[str, Any]]) -> None:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CANDIDATE_SHEET_FIELDS:
            raise GateError("sheet_header")
        sheet_rows = list(reader)
    if len(sheet_rows) != len(decisions):
        raise GateError("sheet_decision_binding")
    for sheet, decision in zip(sheet_rows, decisions):
        if any(
            sheet.get(key, "") != str(decision.get(key, ""))
            for key in CANDIDATE_SHEET_FIELDS
        ):
            raise GateError("sheet_decision_binding")


def _graphql_argv(query: str, variables: dict[str, Any], operation: str) -> list[str]:
    order = {
        "discovery": ("owner", "name", "after"),
        "issue": ("owner", "name", "number", "commentsAfter", "timelineAfter"),
        "fix": ("owner", "name", "oid"),
    }[operation]
    if set(variables) != set(order):
        raise GateError("journal_page_variables")
    argv = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key in order:
        value = variables[key]
        if value is None:
            continue
        flag = "-F" if isinstance(value, int) and not isinstance(value, bool) else "-f"
        argv.extend([flag, f"{key}={value}"])
    return argv


def verify_journal_page_closure(
    *, payload_root: Path, frozen_root: Path, journal: Path
) -> dict[str, Any]:
    journal_path = Path(journal)
    if not journal_path.is_file() or journal_path.is_symlink():
        raise GateError("journal_missing")
    records: list[dict[str, Any]] = []
    for raw_line in journal_path.read_bytes().splitlines(keepends=True):
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"journal_json: {exc}") from exc
        if raw_line != _common.canonical_json_bytes(record) + b"\n":
            raise GateError("journal_not_canonical")
        records.append(record)
    if [row.get("sequence") for row in records] != list(range(1, len(records) + 1)):
        raise GateError("journal_sequence")
    pages = _load_json(Path(payload_root) / "PAGE_MANIFESTS.json", "page_manifests").get("pages")
    if not isinstance(pages, list):
        raise GateError("page_manifests")
    page_by_key: dict[str, dict[str, Any]] = {}
    for page in pages:
        request_key = page.get("request_key") if isinstance(page, dict) else None
        if not isinstance(request_key, str) or not request_key or request_key in page_by_key:
            raise GateError("page_request_key")
        page_by_key[request_key] = page
    intent_rows = [
        row for row in records
        if row.get("stage") == "request_intent" and row.get("evidence_request") is True
    ]
    command_rows = [
        row for row in records
        if row.get("stage") == "command" and row.get("evidence_request") is True
    ]
    intents = {row.get("request_key"): row for row in intent_rows}
    commands = {row.get("request_key"): row for row in command_rows}
    if (
        len(intent_rows) != len(page_by_key)
        or len(command_rows) != len(page_by_key)
        or len(intents) != len(page_by_key)
        or len(commands) != len(page_by_key)
        or set(intents) != set(page_by_key)
        or set(commands) != set(page_by_key)
    ):
        raise GateError("journal_page_key_closure")
    transport = _load_json(Path(frozen_root) / "TRANSPORT_CONTRACT.json", "transport")
    operation_names = {"discovery": "discovery", "issue": "issue_evidence", "fix": "fix_evidence"}
    query_text: dict[str, str] = {}
    for kind, operation in operation_names.items():
        binding = transport.get("query_files", {}).get(operation, {})
        query_path = Path(frozen_root).parents[2] / str(binding.get("path", ""))
        query_text[kind] = query_path.read_text(encoding="utf-8")
    for request_key, page in page_by_key.items():
        intent = intents[request_key]
        command = commands[request_key]
        expected_argv = _graphql_argv(query_text[page["kind"]], page["variables"], page["kind"])
        if (
            intent.get("argv") != expected_argv
            or command.get("argv") != expected_argv
            or command.get("sequence") != intent.get("sequence") + 1
            or command.get("exit_code") != 0
            or command.get("stdout_sha256") != page.get("response_sha256")
            or command.get("runner_state") != "active"
        ):
            raise GateError(f"journal_page_binding: {request_key}")
    if any(row.get("runner_state") == "terminal" for row in records):
        raise GateError("journal_terminal")
    return {
        "evidence_request_count": len(page_by_key),
        "journal_record_count": len(records),
        "journal_sha256": hashlib.sha256(journal_path.read_bytes()).hexdigest(),
    }


def verify_decision_uniqueness(decisions: Sequence[dict[str, Any]]) -> None:
    seen: dict[str, set[Any]] = {
        "neutral_id": set(),
        "issue_node_id": set(),
        "repository_issue_number": set(),
        "issue_url": set(),
        "fixed_sha": set(),
        "issue_fix_pair": set(),
    }
    for row in decisions:
        values = {
            "neutral_id": row.get("neutral_id"),
            "issue_node_id": row.get("id") or row.get("issue_node_id"),
            "repository_issue_number": (row.get("repository"), row.get("number") or row.get("issue_number")),
            "issue_url": row.get("url") or row.get("issue_url"),
            "fixed_sha": row.get("fixed_sha"),
            "issue_fix_pair": (row.get("url") or row.get("issue_url"), row.get("fixed_sha")),
        }
        for key in ("neutral_id", "issue_node_id", "repository_issue_number", "issue_url"):
            value = values[key]
            if value in (None, "", (None, None)):
                raise GateError(f"decision_unique_key_missing: {key}")
            if value in seen[key]:
                raise GateError(f"decision_duplicate: {key}")
            seen[key].add(value)
        fixed_sha = values["fixed_sha"]
        if row.get("decision") == "ADMIT_PENDING_REPRO" and not fixed_sha:
            raise GateError("decision_unique_key_missing: fixed_sha")
        if fixed_sha:
            for key in ("fixed_sha", "issue_fix_pair"):
                value = values[key]
                if value in seen[key]:
                    raise GateError(f"decision_duplicate: {key}")
                seen[key].add(value)


def validate_decision(row: dict[str, Any]) -> None:
    admitted = row.get("crit_real_public_fix") == "PASS" and row.get("crit_in_numerical_scope") == "PASS"
    if (row.get("decision") == "ADMIT_PENDING_REPRO") != admitted:
        raise GateError("decision_biconditional")
    if row.get("crit_dual_arm_repro") != "PENDING":
        raise GateError("a2_not_pending")
    if row.get("analysis_id") != "" or row.get("alias") != "":
        raise GateError("blind_fields")


def verify_quota_results(results: dict[str, int]) -> None:
    if results != EXPECTED_QUOTAS:
        raise GateError(f"quota_vector: {results!r}")


def verify_five_layer_binding(chain: dict[str, dict[str, Any]]) -> None:
    snapshot = chain.get("snapshot", {})
    expected = (snapshot.get("record_id"), snapshot.get("sha256"))
    if not all(expected):
        raise GateError("five_layer_binding")
    for name in ("queue", "decision", "sheet", "evidence"):
        layer = chain.get(name, {})
        if (layer.get("snapshot_record_id"), layer.get("snapshot_record_sha256")) != expected:
            raise GateError(f"five_layer_binding: {name}")


def verify_candidate_path_set(actual: set[str], expected: set[str]) -> None:
    if actual != expected:
        raise GateError(f"candidate_path_set: actual={sorted(actual)!r} expected={sorted(expected)!r}")


def verify_exact_manifest_projection(
    manifest: dict[str, Any], expected: dict[str, Any]
) -> None:
    if set(manifest) != set(expected) or manifest != expected:
        raise GateError("payload_manifest_binding")


def _candidate_payload_paths(payload_root: Path) -> set[str]:
    pages = _load_json(Path(payload_root) / "PAGE_MANIFESTS.json", "page_manifests").get("pages")
    artifacts = _load_json(
        Path(payload_root) / "EVIDENCE_SNAPSHOT.json", "evidence_snapshot"
    ).get("artifacts")
    if not isinstance(pages, list) or not isinstance(artifacts, list):
        raise GateError("candidate_manifest_paths")
    dynamic = [page.get("path") for page in pages] + [item.get("path") for item in artifacts]
    if any(
        not isinstance(path, str)
        or not path
        or Path(path).is_absolute()
        or ".." in Path(path).parts
        for path in dynamic
    ):
        raise GateError("candidate_manifest_paths")
    return set(REQUIRED_PAYLOAD_FILES) | set(dynamic)


def handle_verify_payload(
    *, root: Path, candidate_root: Path, authority: str, journal: Path, branch: str | None = None
) -> int:
    if branch is not None and branch != EVIDENCE_BRANCH:
        raise GateError("evidence_branch")
    if not re.fullmatch(r"[0-9a-f]{40}", authority):
        raise GateError("authority_sha")
    payload_root = Path(candidate_root) / PAYLOAD_REL
    if not payload_root.is_dir() or payload_root.is_symlink():
        raise GateError("candidate_payload_root")
    actual = {
        path.relative_to(payload_root).as_posix()
        for path in payload_root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if not REQUIRED_PAYLOAD_FILES.issubset(actual):
        raise GateError(f"candidate_path_set: missing={sorted(REQUIRED_PAYLOAD_FILES - actual)!r}")
    for relative in actual:
        allowed = relative in REQUIRED_PAYLOAD_FILES | OPTIONAL_PAYLOAD_FILES or bool(
            re.fullmatch(
                r"(?:transport_pages/[^/]+\.json|issue_pages/[^/]+/issue_page_\d{4}\.json|"
                r"fix_pages/[^/]+/fix_page_\d{4}\.json|admission_evidence/[^/]+/evidence\.json)",
                relative,
            )
        )
        if not allowed:
            raise GateError(f"candidate_path_set: forbidden={relative}")
    for relative in REQUIRED_PAYLOAD_FILES:
        path = payload_root / relative
        if not path.is_file() or path.is_symlink():
            raise GateError(f"candidate_file: {relative}")
    try:
        decisions = json.loads((payload_root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"review_decisions_json: {exc}") from exc
    rows = decisions.get("rows") if isinstance(decisions, dict) else None
    if not isinstance(rows, list):
        raise GateError("review_decisions_rows")
    quotas = {repo: 0 for repo in EXPECTED_QUOTAS}
    for row in rows:
        if not isinstance(row, dict):
            raise GateError("review_decision_row")
        if row.get("decision") != "ADMIT_PENDING_REPRO":
            continue
        repository = row.get("repository")
        if repository not in quotas:
            raise GateError("review_decision_repository")
        quotas[repository] += 1
    verify_quota_results(quotas)
    replay = reconstruct_from_raw(
        payload_root, frozen_root=Path(root) / "data/external_slice/supplemental_r3"
    )
    if replay["quota_results"] != quotas:
        raise GateError("independent_replay_quota")
    verify_journal_page_closure(
        payload_root=payload_root,
        frozen_root=Path(root) / "data/external_slice/supplemental_r3",
        journal=Path(journal),
    )
    root_path = Path(root)
    if (root_path / ".git").exists() and Path(journal).is_file():
        runner = _common.TerminalCommandRunner(Path(journal))
        bundle_path = (
            root_path / "data/external_slice/supplemental_r3/"
            "EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"
        )
        bundle = _load_json(bundle_path, "bundle_manifest")
        seal_path = root_path / VM_SEAL_REL
        seal_raw = seal_path.read_bytes()
        seal = _load_json(seal_path, "pre_network_seal")
        _verify_environment_journal_provenance(
            root=root_path,
            journal=Path(journal),
            seal=seal,
            bundle=bundle,
            seal_sha256=hashlib.sha256(seal_raw).hexdigest(),
            seal_raw=seal_raw,
        )
        bindings = bundle.get("frozen_inputs", {})
        frozen = _common.verify_frozen_inputs(
            root=root_path,
            authority=authority,
            runner=runner,
            expected_r2_entries=bindings.get("r2_entries"),
            expected_original_r3_entries=bindings.get("original_r3_entries"),
            expected_admission_sheet=bindings.get("admission_sheet"),
        )
        if not frozen.get("batch3_deny_consistent"):
            raise GateError("batch3_deny_consistency")
    manifest_path = payload_root / PAYLOAD_MANIFEST
    if manifest_path.exists():
        verify_payload_manifest_exact(
            root=Path(root),
            payload_root=payload_root,
            authority=authority,
            journal=Path(journal),
        )
    return 0


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _read_vm_seal_commit(
    *,
    root: Path,
    journal: Path,
    seal: dict[str, Any],
    expected_commit: str | None = None,
) -> str:
    runner = _common.TerminalCommandRunner(Path(journal))
    root_text = str(Path(root))
    if expected_commit is None:
        head_raw, _ = runner.run(["git", "-C", root_text, "rev-parse", "HEAD"])
        seal_commit = head_raw.decode("ascii").strip()
    else:
        seal_commit = expected_commit
    history_raw, _ = runner.run([
        "git", "-C", root_text, "rev-list", "--parents", "-n", "1", seal_commit
    ])
    fields = history_raw.decode("ascii").strip().split()
    changed_raw, _ = runner.run([
        "git", "-C", root_text, "diff-tree", "--no-commit-id", "--name-only", "-r", seal_commit
    ])
    changed = [line for line in changed_raw.decode("utf-8").splitlines() if line]
    if fields != [seal_commit, seal.get("bundle_commit")] or changed != [VM_SEAL_REL.as_posix()]:
        raise GateError("pre_network_seal_history")
    committed_raw, _ = runner.run([
        "git", "-C", root_text, "show", f"{seal_commit}:{VM_SEAL_REL.as_posix()}"
    ])
    if committed_raw != (Path(root) / VM_SEAL_REL).read_bytes():
        raise GateError("pre_network_seal_committed_bytes")
    return seal_commit


def _journal_prefix_state(
    journal: Path, record_count: int, *, final_operation_name: str | None = None
) -> dict[str, Any]:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    if not isinstance(record_count, int) or record_count <= 0 or record_count > len(lines):
        raise GateError("journal_prefix_count")
    records: list[dict[str, Any]] = []
    for line in lines[:record_count]:
        try:
            record = json.loads(line.decode("utf-8"))
        except Exception as exc:
            raise GateError(f"journal_prefix_json: {exc}") from exc
        if line != _common.canonical_json_bytes(record) + b"\n":
            raise GateError("journal_prefix_canonical")
        records.append(record)
    if [record.get("sequence") for record in records] != list(range(1, record_count + 1)):
        raise GateError("journal_prefix_sequence")
    request_keys = {
        record.get("request_key")
        for record in records
        if record.get("stage") == "command" and record.get("evidence_request") is True
    }
    if None in request_keys or any(record.get("runner_state") == "terminal" for record in records):
        raise GateError("journal_prefix_state")
    if final_operation_name is not None:
        operation_names = {
            record.get("operation_key"): record.get("operation_name")
            for record in records
            if record.get("stage") == "operation_intent"
        }
        final = records[-1]
        if (
            final.get("stage") != "operation"
            or operation_names.get(final.get("operation_key")) != final_operation_name
        ):
            raise GateError("journal_acquisition_boundary")
    raw = b"".join(lines[:record_count])
    return {
        "journal_record_count": record_count,
        "journal_sha256": hashlib.sha256(raw).hexdigest(),
        "evidence_request_count": len(request_keys),
    }


def _candidate_collection_prefix_state(journal: Path) -> dict[str, Any]:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    records = [json.loads(line.decode("utf-8")) for line in lines]
    intents = [
        record
        for record in records
        if record.get("stage") == "operation_intent"
        and record.get("operation_name") == "candidate_collection"
    ]
    if len(intents) != 1:
        raise GateError("candidate_collection_intent")
    operation_key = intents[0].get("operation_key")
    candidate_index = records.index(intents[0])
    environment_intents = [
        record
        for record in records
        if record.get("stage") == "operation_intent"
        and record.get("operation_name") == "verify_environment_seal"
    ]
    if len(environment_intents) != 1 or candidate_index < 3:
        raise GateError("candidate_collection_environment_boundary")
    environment_completion, head_record, status_record = records[candidate_index - 3:candidate_index]
    candidate_metadata = intents[0].get("metadata", {})
    environment_metadata = environment_completion.get("metadata", {})
    root_argv = head_record.get("argv", [])
    root_text = root_argv[2] if len(root_argv) >= 3 else None
    seal_commit = candidate_metadata.get("environment_seal_commit")
    seal_sha256 = candidate_metadata.get("environment_seal_sha256")
    if (
        environment_completion.get("stage") != "operation"
        or environment_completion.get("operation_key")
        != environment_intents[0].get("operation_key")
        or records.index(environment_completion)
        != records.index(environment_intents[0]) + 1
        or environment_metadata.get("seal_commit") != seal_commit
        or environment_metadata.get("seal_sha256") != seal_sha256
        or not re.fullmatch(r"[0-9a-f]{40}", str(seal_commit or ""))
        or not re.fullmatch(r"[0-9a-f]{64}", str(seal_sha256 or ""))
        or head_record.get("stage") != "command"
        or head_record.get("argv") != ["git", "-C", root_text, "rev-parse", "HEAD"]
        or head_record.get("stdout_sha256")
        != hashlib.sha256((str(seal_commit) + "\n").encode("ascii")).hexdigest()
        or head_record.get("exit_code") != 0
        or status_record.get("stage") != "command"
        or status_record.get("argv")
        != ["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"]
        or status_record.get("stdout_sha256") != hashlib.sha256(b"").hexdigest()
        or status_record.get("exit_code") != 0
    ):
        raise GateError("candidate_collection_environment_boundary")
    completions = [
        record
        for record in records
        if record.get("stage") == "operation" and record.get("operation_key") == operation_key
    ]
    if len(completions) != 1:
        raise GateError("candidate_collection_completion")
    record_count = completions[0].get("sequence")
    state = _journal_prefix_state(
        Path(journal), record_count, final_operation_name="candidate_collection"
    )
    if any(record.get("evidence_request") is True for record in records[record_count:]):
        raise GateError("evidence_request_after_collection")
    return state


def _git_tree_bytes(entries: Sequence[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            f'{entry["mode"]} {entry["type"]} {entry["oid"]}\t{entry["path"]}'
        ).encode("utf-8") + b"\0"
        for entry in entries
    )


def _expected_environment_command_trace(
    *, root: Path, seal: dict[str, Any], bundle: dict[str, Any],
    seal_commit: str, seal_raw: bytes,
) -> list[tuple[list[str], bytes | str]]:
    root_text = str(Path(root))
    authority = str(seal.get("authority"))
    bundle_commit = str(seal.get("bundle_commit"))
    bundle_tree = str(seal.get("bundle_tree"))
    commits = bundle.get("commits", {})
    red = str(commits.get("red", {}).get("commit", ""))
    green = str(commits.get("green", {}).get("commit", ""))
    authority_tree = str(bundle.get("authority_tree", ""))
    frozen = bundle.get("frozen_inputs", {})
    r2_entries = frozen.get("r2_entries")
    original_r3 = frozen.get("original_r3_entries")
    admission = frozen.get("admission_sheet")
    if (
        not all(re.fullmatch(r"[0-9a-f]{40}", item) for item in (
            authority, bundle_commit, bundle_tree, red, green, authority_tree, seal_commit
        ))
        or not isinstance(r2_entries, list) or len(r2_entries) != 634
        or not isinstance(original_r3, list) or len(original_r3) != 12
        or not isinstance(admission, dict)
        or not re.fullmatch(r"[0-9a-f]{40}", str(admission.get("blob", "")))
        or not re.fullmatch(r"[0-9a-f]{64}", str(admission.get("sha256", "")))
    ):
        raise GateError("environment_journal_provenance")
    for entry in [*r2_entries, *original_r3]:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"path", "mode", "type", "oid", "sha256"}
            or not isinstance(entry.get("path"), str)
            or entry.get("mode") not in {"100644", "100755", "120000"}
            or entry.get("type") != "blob"
            or not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("oid", "")))
            or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", "")))
        ):
            raise GateError("environment_journal_provenance")

    def git(*args: str) -> list[str]:
        return ["git", "-C", root_text, *args]

    trace: list[tuple[list[str], bytes | str]] = [
        (git("rev-parse", "HEAD"), (seal_commit + "\n").encode("ascii")),
        (git("rev-list", "--parents", "-n", "1", seal_commit), (seal_commit + " " + bundle_commit + "\n").encode("ascii")),
        (git("diff-tree", "--no-commit-id", "--name-only", "-r", seal_commit), (VM_SEAL_REL.as_posix() + "\n").encode("utf-8")),
        (git("show", f"{seal_commit}:{VM_SEAL_REL.as_posix()}"), seal_raw),
        (git("show", "-s", "--format=%s", seal_commit), b"evidence(external): seal Supplemental R3 environment\n"),
        (git("status", "--porcelain=v1", "--untracked-files=all"), b""),
        (git("rev-parse", "HEAD"), (seal_commit + "\n").encode("ascii")),
        (git("rev-parse", f"{bundle_commit}^{{tree}}"), (bundle_tree + "\n").encode("ascii")),
        (git("rev-list", "--parents", "-n", "1", red), (red + " " + authority + "\n").encode("ascii")),
        (git("rev-list", "--parents", "-n", "1", green), (green + " " + red + "\n").encode("ascii")),
        (git("rev-list", "--parents", "-n", "1", bundle_commit), (bundle_commit + " " + green + "\n").encode("ascii")),
        (git("rev-parse", f"{authority}^{{tree}}"), (authority_tree + "\n").encode("ascii")),
    ]
    for commit, paths in (
        (red, BUNDLE_RED_PATHS), (green, BUNDLE_GREEN_PATHS),
        (bundle_commit, BUNDLE_SEAL_PATHS),
    ):
        trace.append((
            git("diff-tree", "--no-commit-id", "--name-only", "-r", commit),
            ("".join(f"{path}\n" for path in sorted(paths))).encode("utf-8"),
        ))
    trace.extend([
        (git("status", "--porcelain=v1", "--untracked-files=all"), b""),
        (git("rev-parse", f"{authority}:data/external_slice/supplemental_r2"), b"2e8fe75233bed73c9facb1c66b5d72b6a172487d\n"),
        (git("ls-tree", "-r", "-z", authority, "--", "data/external_slice/supplemental_r2"), _git_tree_bytes(r2_entries)),
    ])
    trace.extend(
        (git("show", f'{authority}:{entry["path"]}'), str(entry["sha256"]))
        for entry in r2_entries
    )
    trace.extend([
        (git("rev-parse", f"{authority}:data/external_slice/admission_sheet.csv"), (str(admission["blob"]) + "\n").encode("ascii")),
        (git("show", f"{authority}:data/external_slice/admission_sheet.csv"), str(admission["sha256"])),
        (git("ls-tree", "-r", "-z", authority, "--", "data/external_slice/supplemental_r3"), _git_tree_bytes(original_r3)),
    ])
    trace.extend(
        (git("show", f'{authority}:{entry["path"]}'), str(entry["sha256"]))
        for entry in original_r3
    )
    trace.extend([
        (git("diff", "--quiet", authority, "--", "data/external_slice/supplemental_r2", "data/external_slice/admission_sheet.csv"), b""),
        (git("status", "--porcelain=v1", "--untracked-files=all", "--", "data/external_slice/supplemental_r2", "data/external_slice/admission_sheet.csv"), b""),
    ])
    return trace


def _verify_environment_journal_provenance(
    *, root: Path, journal: Path, seal: dict[str, Any], bundle: dict[str, Any],
    seal_sha256: str, seal_raw: bytes,
) -> None:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    try:
        records = [json.loads(line.decode("utf-8")) for line in lines]
    except Exception as exc:
        raise GateError(f"environment_journal_provenance: {exc}") from exc
    if (
        any(line != _common.canonical_json_bytes(record) + b"\n" for line, record in zip(lines, records, strict=True))
        or [record.get("sequence") for record in records] != list(range(1, len(records) + 1))
    ):
        raise GateError("environment_journal_provenance")
    count = seal.get("journal_record_count")
    if not isinstance(count, int) or count <= 0 or len(records) <= count + 7:
        raise GateError("environment_journal_provenance")
    intent = records[count - 1]
    completion, add_record, commit_record = records[count:count + 3]
    if (
        hashlib.sha256(b"".join(lines[:count])).hexdigest() != seal.get("journal_prefix_sha256")
        or intent.get("stage") != "operation_intent"
        or intent.get("operation_name") != "materialize_pre_network_seal"
        or completion.get("stage") != "operation"
        or completion.get("operation_key") != intent.get("operation_key")
        or completion.get("metadata") != {"sha256": seal_sha256}
        or completion.get("evidence_request") is not False
        or completion.get("runner_state") != "active"
        or add_record.get("stage") != "command"
        or add_record.get("argv") != ["git", "add", VM_SEAL_REL.as_posix()]
        or add_record.get("exit_code") != 0
        or add_record.get("evidence_request") is not False
        or add_record.get("runner_state") != "active"
        or commit_record.get("stage") != "command"
        or commit_record.get("argv") != list(ENVIRONMENT_SEAL_COMMIT_COMMAND)
        or commit_record.get("exit_code") != 0
        or commit_record.get("evidence_request") is not False
        or commit_record.get("runner_state") != "active"
    ):
        raise GateError("environment_journal_provenance")
    candidate_intents = [
        (index, record) for index, record in enumerate(records)
        if record.get("stage") == "operation_intent"
        and record.get("operation_name") == "candidate_collection"
    ]
    if len(candidate_intents) != 1:
        raise GateError("environment_journal_provenance")
    if sum(
        record.get("stage") == "operation_intent"
        and record.get("operation_name") == "materialize_pre_network_seal"
        for record in records
    ) != 1 or sum(
        record.get("stage") == "operation_intent"
        and record.get("operation_name") == "verify_environment_seal"
        for record in records
    ) != 1:
        raise GateError("environment_journal_provenance")
    candidate_index, candidate_intent = candidate_intents[0]
    trace = _expected_environment_command_trace(
        root=Path(root), seal=seal, bundle=bundle,
        seal_commit=str(candidate_intent.get("metadata", {}).get("environment_seal_commit", "")),
        seal_raw=seal_raw,
    )
    trace_start = count + 3
    trace_end = trace_start + len(trace)
    if candidate_index != trace_end + 4:
        raise GateError("environment_journal_provenance")
    for record, (argv, stdout) in zip(records[trace_start:trace_end], trace, strict=True):
        expected_stdout_sha = (
            stdout if isinstance(stdout, str) else hashlib.sha256(stdout).hexdigest()
        )
        if (
            record.get("stage") != "command"
            or record.get("argv") != argv
            or record.get("exit_code") != 0
            or record.get("stdout_sha256") != expected_stdout_sha
            or record.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
            or record.get("evidence_request") is not False
            or record.get("runner_state") != "active"
        ):
            raise GateError("environment_journal_provenance")
    environment_intent, environment_completion, head_record, status_record = records[trace_end:candidate_index]
    seal_commit = str(candidate_intent.get("metadata", {}).get("environment_seal_commit", ""))
    expected_frozen = {
        "r2_tree": "2e8fe75233bed73c9facb1c66b5d72b6a172487d",
        "r2_path_count": 634,
        "admission_blob": "5ef073d4d6297639695491c46d20733236bede52",
        "batch3_deny_consistent": True,
    }
    expected_environment_metadata = {
        "seal_commit": seal_commit,
        "seal_sha256": seal_sha256,
        "vm_green_report_sha256": seal.get("vm_green_report_sha256"),
        "frozen_inputs": expected_frozen,
        "evidence_request_count": 0,
    }
    root_text = str(Path(root))
    candidate_metadata = candidate_intent.get("metadata", {})
    if (
        environment_intent.get("stage") != "operation_intent"
        or environment_intent.get("operation_name") != "verify_environment_seal"
        or environment_intent.get("metadata") != {"seal_commit": seal_commit, "seal_sha256": seal_sha256}
        or environment_intent.get("evidence_request") is not False
        or environment_intent.get("runner_state") != "pending"
        or environment_completion.get("stage") != "operation"
        or environment_completion.get("operation_key") != environment_intent.get("operation_key")
        or environment_completion.get("metadata") != expected_environment_metadata
        or environment_completion.get("evidence_request") is not False
        or environment_completion.get("runner_state") != "active"
        or head_record.get("stage") != "command"
        or head_record.get("argv") != ["git", "-C", root_text, "rev-parse", "HEAD"]
        or head_record.get("stdout_sha256") != hashlib.sha256((seal_commit + "\n").encode("ascii")).hexdigest()
        or head_record.get("exit_code") != 0
        or head_record.get("evidence_request") is not False
        or head_record.get("runner_state") != "active"
        or status_record.get("stage") != "command"
        or status_record.get("argv") != ["git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all"]
        or status_record.get("stdout_sha256") != hashlib.sha256(b"").hexdigest()
        or status_record.get("exit_code") != 0
        or status_record.get("evidence_request") is not False
        or status_record.get("runner_state") != "active"
        or candidate_metadata.get("authority") != seal.get("authority")
        or candidate_metadata.get("environment_seal_commit") != seal_commit
        or candidate_metadata.get("environment_seal_sha256") != seal_sha256
        or candidate_intent.get("evidence_request") is not False
        or candidate_intent.get("runner_state") != "pending"
    ):
        raise GateError("environment_journal_provenance")


def _verify_pre_network_seal_operation_completion(
    *, journal: Path, seal: dict[str, Any], seal_sha256: str
) -> None:
    lines = Path(journal).read_bytes().splitlines(keepends=True)
    count = seal.get("journal_record_count")
    if not isinstance(count, int) or count <= 0 or count >= len(lines):
        raise GateError("pre_network_operation_boundary")
    try:
        intent = json.loads(lines[count - 1].decode("utf-8"))
        completion = json.loads(lines[count].decode("utf-8"))
    except Exception as exc:
        raise GateError(f"pre_network_operation_json: {exc}") from exc
    if (
        lines[count - 1] != _common.canonical_json_bytes(intent) + b"\n"
        or lines[count] != _common.canonical_json_bytes(completion) + b"\n"
        or intent.get("stage") != "operation_intent"
        or intent.get("operation_name") != "materialize_pre_network_seal"
        or completion.get("stage") != "operation"
        or completion.get("operation_key") != intent.get("operation_key")
        or completion.get("sequence") != count + 1
        or completion.get("metadata") != {"sha256": seal_sha256}
        or completion.get("evidence_request") is not False
        or completion.get("runner_state") != "active"
    ):
        raise GateError("pre_network_operation_boundary")


def _expected_payload_manifest(
    *,
    authority: str,
    seal: dict[str, Any],
    pre_network_seal_commit: str,
    pre_network_seal_sha256: str,
    journal_state: dict[str, Any],
    candidate_file_sha256: dict[str, str],
) -> dict[str, Any]:
    return {
        "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03",
        "authority": authority,
        "bundle_commit": seal["bundle_commit"],
        "bundle_tree": seal["bundle_tree"],
        "bundle_manifest_sha256": seal["bundle_manifest_sha256"],
        "design_sha256": seal["design_sha256"],
        "pre_network_seal_commit": pre_network_seal_commit,
        "pre_network_seal_sha256": pre_network_seal_sha256,
        "spool_sha256": seal["spool_sha256"],
        "vm_green_report_sha256": seal["vm_green_report_sha256"],
        "vm_green": seal["vm_green"],
        "environment_seal_commit_command": seal["environment_seal_commit_command"],
        "plan_sha256": seal["plan_sha256"],
        "pre_network_journal_prefix_sha256": seal["journal_prefix_sha256"],
        "pre_network_journal_record_count": seal["journal_record_count"],
        "journal_sha256": journal_state["journal_sha256"],
        "journal_record_count": journal_state["journal_record_count"],
        "quota_results": EXPECTED_QUOTAS,
        "candidate_file_sha256": candidate_file_sha256,
        "pre_network_evidence_request_count": seal.get("evidence_request_count", 0),
        "evidence_request_count": journal_state["evidence_request_count"],
        "verdict": "SUPPLEMENTAL_R3_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03_EVIDENCE_HANDOFF_PENDING_LOCAL_AUDIT",
        "research_evidence_boundary": {
            "candidate_evidence_only": True,
            "manuscript_claims_unmodified": True,
            "requires_separate_local_desktop_evidence_audit_pass": True,
        },
        "terminal_commands": [
            list(PAYLOAD_COMMIT_COMMAND),
            list(HANDOFF_COMMIT_COMMAND),
            list(PUSH_COMMAND),
        ],
    }


def verify_payload_manifest_exact(
    *,
    root: Path,
    payload_root: Path,
    authority: str,
    journal: Path,
) -> dict[str, Any]:
    manifest_path = Path(payload_root) / PAYLOAD_MANIFEST
    raw = manifest_path.read_bytes()
    manifest = _load_json(manifest_path, "payload_manifest")
    if raw != _common.canonical_json_bytes(manifest) + b"\n":
        raise GateError("payload_manifest_canonical")
    seal_path = Path(root) / VM_SEAL_REL
    seal = _load_json(seal_path, "pre_network_seal")
    seal_sha256 = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    embedded_vm_report = seal.get("vm_green_report")
    if (
        not re.fullmatch(r"[0-9a-f]{64}", str(seal.get("vm_green_report_sha256", "")))
        or not isinstance(embedded_vm_report, dict)
        or hashlib.sha256(
            _common.canonical_json_bytes(embedded_vm_report) + b"\n"
        ).hexdigest()
        != seal.get("vm_green_report_sha256")
        or embedded_vm_report.get("phase") != "green"
        or embedded_vm_report.get("vm_run") is not True
        or embedded_vm_report.get("evidence_request_count") != 0
        or not isinstance(embedded_vm_report.get("records"), list)
        or not embedded_vm_report["records"]
        or any(row.get("outcome") != "PASS" for row in embedded_vm_report["records"])
        or embedded_vm_report.get("full_suite_network_spy_count") != 0
        or seal.get("vm_green") != {
            "node_count": len(embedded_vm_report["records"]),
            "full_suite": embedded_vm_report.get("full_suite"),
            "evidence_request_count": 0,
        }
        or seal.get("environment_seal_commit_command")
        != list(ENVIRONMENT_SEAL_COMMIT_COMMAND)
        or not isinstance(seal.get("vm_green"), dict)
        or seal["vm_green"].get("evidence_request_count") != 0
        or not isinstance(seal["vm_green"].get("node_count"), int)
        or seal["vm_green"].get("node_count", 0) <= 0
        or not isinstance(seal["vm_green"].get("full_suite"), dict)
        or seal["vm_green"]["full_suite"].get("passed", 0) <= 0
    ):
        raise GateError("vm_green_binding")
    bundle_path = (
        Path(root)
        / "data/external_slice/supplemental_r3/"
        "EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json"
    )
    bundle = _load_json(bundle_path, "bundle_manifest")
    if (
        hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        != seal.get("bundle_manifest_sha256")
        or bundle.get("authority") != authority
        or bundle.get("design_sha256") != seal.get("design_sha256")
        or bundle.get("parent_plan_sha256") != seal.get("plan_sha256", [])[:3]
    ):
        raise GateError("payload_bundle_binding")
    _verify_environment_journal_provenance(
        root=Path(root),
        journal=Path(journal),
        seal=seal,
        bundle=bundle,
        seal_sha256=seal_sha256,
        seal_raw=seal_path.read_bytes(),
    )
    seal_commit = _read_vm_seal_commit(
        root=Path(root),
        journal=Path(journal),
        seal=seal,
        expected_commit=manifest.get("pre_network_seal_commit"),
    )
    _verify_pre_network_seal_operation_completion(
        journal=Path(journal), seal=seal, seal_sha256=seal_sha256
    )
    pre_network_state = _journal_prefix_state(
        Path(journal), seal.get("journal_record_count")
    )
    if (
        pre_network_state["journal_sha256"] != seal.get("journal_prefix_sha256")
        or pre_network_state["evidence_request_count"] != 0
    ):
        raise GateError("pre_network_journal_binding")
    acquisition_state = _candidate_collection_prefix_state(Path(journal))
    if acquisition_state["journal_record_count"] != manifest.get("journal_record_count"):
        raise GateError("journal_acquisition_boundary")
    page_state = verify_journal_page_closure(
        payload_root=Path(payload_root),
        frozen_root=Path(root) / "data/external_slice/supplemental_r3",
        journal=Path(journal),
    )
    if acquisition_state["evidence_request_count"] != page_state["evidence_request_count"]:
        raise GateError("payload_journal_binding")
    replay = reconstruct_from_raw(
        Path(payload_root), frozen_root=Path(root) / "data/external_slice/supplemental_r3"
    )
    if replay.get("quota_results") != EXPECTED_QUOTAS:
        raise GateError("payload_replay_binding")
    candidate_paths = _candidate_payload_paths(Path(payload_root))
    file_sha256 = {
        relative: hashlib.sha256((Path(payload_root) / relative).read_bytes()).hexdigest()
        for relative in sorted(candidate_paths)
        if (Path(payload_root) / relative).is_file()
        and not (Path(payload_root) / relative).is_symlink()
    }
    if set(file_sha256) != candidate_paths:
        raise GateError("candidate_manifest_paths")
    actual_paths = {
        path.relative_to(Path(payload_root)).as_posix()
        for path in Path(payload_root).rglob("*")
        if path.is_file() or path.is_symlink()
    }
    repository_payload = Path(payload_root).resolve() == (Path(root) / PAYLOAD_REL).resolve()
    if repository_payload:
        prefix = PAYLOAD_REL.as_posix() + "/"
        original = {
            entry["path"].removeprefix(prefix)
            for entry in bundle.get("frozen_inputs", {}).get("original_r3_entries", [])
        }
        bundle_files = {
            path.removeprefix(prefix)
            for path in bundle.get("allowed_bundle_paths", [])
            if isinstance(path, str) and path.startswith(prefix)
        }
        expected_paths = (
            original
            | bundle_files
            | candidate_paths
            | {PAYLOAD_MANIFEST, VM_SEAL_REL.name}
        )
        handoff_name = "HANDOFF_SUPPLEMENTAL_R3.json"
        if (Path(payload_root) / handoff_name).is_file():
            expected_paths.add(handoff_name)
    else:
        expected_paths = candidate_paths | {PAYLOAD_MANIFEST}
    if actual_paths != expected_paths:
        raise GateError("payload_directory_union")
    expected = _expected_payload_manifest(
        authority=authority,
        seal=seal,
        pre_network_seal_commit=seal_commit,
        pre_network_seal_sha256=seal_sha256,
        journal_state=acquisition_state,
        candidate_file_sha256=file_sha256,
    )
    verify_exact_manifest_projection(manifest, expected)
    return manifest


def handle_build_payload(
    *, root: Path, candidate_root: Path, authority: str, journal: Path, branch: str | None = None
) -> int:
    if branch != EVIDENCE_BRANCH:
        raise GateError("evidence_branch")
    handle_verify_payload(root=root, candidate_root=candidate_root, authority=authority, journal=journal)
    seal_path = Path(root) / VM_SEAL_REL
    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"pre_network_seal: {exc}") from exc
    required = (
        "bundle_commit", "bundle_tree", "bundle_manifest_sha256", "spool_sha256",
        "plan_sha256", "design_sha256", "journal_prefix_sha256", "journal_record_count",
        "vm_green_report_sha256", "vm_green_report", "vm_green",
        "environment_seal_commit_command",
    )
    if any(key not in seal for key in required):
        raise GateError("pre_network_seal_binding")
    embedded_vm_report = seal.get("vm_green_report")
    if (
        not re.fullmatch(r"[0-9a-f]{64}", str(seal.get("vm_green_report_sha256", "")))
        or not isinstance(embedded_vm_report, dict)
        or hashlib.sha256(
            _common.canonical_json_bytes(embedded_vm_report) + b"\n"
        ).hexdigest()
        != seal.get("vm_green_report_sha256")
        or embedded_vm_report.get("phase") != "green"
        or embedded_vm_report.get("vm_run") is not True
        or embedded_vm_report.get("evidence_request_count") != 0
        or not isinstance(embedded_vm_report.get("records"), list)
        or not embedded_vm_report["records"]
        or any(row.get("outcome") != "PASS" for row in embedded_vm_report["records"])
        or embedded_vm_report.get("full_suite_network_spy_count") != 0
        or seal.get("vm_green") != {
            "node_count": len(embedded_vm_report["records"]),
            "full_suite": embedded_vm_report.get("full_suite"),
            "evidence_request_count": 0,
        }
        or seal.get("environment_seal_commit_command")
        != list(ENVIRONMENT_SEAL_COMMIT_COMMAND)
        or not isinstance(seal.get("vm_green"), dict)
        or seal["vm_green"].get("evidence_request_count") != 0
        or not isinstance(seal["vm_green"].get("node_count"), int)
        or seal["vm_green"].get("node_count", 0) <= 0
        or not isinstance(seal["vm_green"].get("full_suite"), dict)
        or seal["vm_green"]["full_suite"].get("passed", 0) <= 0
    ):
        raise GateError("vm_green_binding")
    pre_network_seal_commit = _read_vm_seal_commit(root=Path(root), journal=Path(journal), seal=seal)
    seal_sha256 = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    _verify_pre_network_seal_operation_completion(
        journal=Path(journal), seal=seal, seal_sha256=seal_sha256
    )
    payload_root = Path(candidate_root) / PAYLOAD_REL
    page_state = verify_journal_page_closure(
        payload_root=payload_root,
        frozen_root=Path(root) / "data/external_slice/supplemental_r3",
        journal=Path(journal),
    )
    journal_state = _candidate_collection_prefix_state(Path(journal))
    if journal_state["evidence_request_count"] != page_state["evidence_request_count"]:
        raise GateError("payload_journal_binding")
    output = payload_root / PAYLOAD_MANIFEST
    if output.exists() or output.is_symlink():
        raise GateError("payload_manifest_exists")
    candidate_paths = _candidate_payload_paths(payload_root)
    file_sha256 = {
        relative: hashlib.sha256((payload_root / relative).read_bytes()).hexdigest()
        for relative in sorted(candidate_paths)
    }
    manifest = _expected_payload_manifest(
        authority=authority,
        seal=seal,
        pre_network_seal_commit=pre_network_seal_commit,
        pre_network_seal_sha256=seal_sha256,
        journal_state=journal_state,
        candidate_file_sha256=file_sha256,
    )
    runner = _common.TerminalCommandRunner(Path(journal))
    operation_key = runner.begin_operation(
        "build_payload_manifest", {"output": str(output), "authority": authority}
    )
    _common.atomic_write_bytes(output, _canonical_bytes(manifest) + b"\n")
    runner.complete_operation(
        operation_key, {"sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    )
    return 0


def handle_publish_payload(
    *, root: Path, candidate_root: Path, authority: str, journal: Path, branch: str | None = None
) -> int:
    if branch != EVIDENCE_BRANCH:
        raise GateError("evidence_branch")
    handle_verify_payload(
        root=root,
        candidate_root=candidate_root,
        authority=authority,
        journal=journal,
        branch=branch,
    )
    candidate_root = Path(candidate_root)
    paths = [
        path.relative_to(candidate_root).as_posix()
        for path in sorted((candidate_root / PAYLOAD_REL).rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    if not paths or not any(path.endswith(PAYLOAD_MANIFEST) for path in paths):
        raise GateError("payload_manifest_missing")
    runner = _common.TerminalCommandRunner(Path(journal))
    if (Path(root) / ".git").exists():
        manifest = _load_json(
            candidate_root / PAYLOAD_REL / PAYLOAD_MANIFEST, "payload_manifest"
        )
        head_raw, _ = runner.run(["git", "-C", str(Path(root)), "rev-parse", "HEAD"])
        status_raw, _ = runner.run([
            "git", "-C", str(Path(root)), "status", "--porcelain=v1", "--untracked-files=all"
        ])
        if head_raw.decode("ascii").strip() != manifest.get("pre_network_seal_commit"):
            raise GateError("publication_head")
        if status_raw:
            raise GateError("publication_worktree_drift")
    operation_key = runner.begin_operation(
        "publish_candidate", {"path_count": len(paths), "authority": authority}
    )
    publish_payload_directory_atomically(
        candidate_root / PAYLOAD_REL, Path(root) / PAYLOAD_REL
    )
    if not all((Path(root) / relative).is_file() for relative in paths):
        raise GateError("publication_incomplete")
    runner.complete_operation(operation_key, {"published_path_count": len(paths)})
    return 0


def _atomic_exchange_directories(left: Path, right: Path) -> None:
    if sys.platform != "linux":
        raise GateError("atomic_exchange_platform")
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise GateError("atomic_exchange_unavailable")
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    result = renameat2(-100, os.fsencode(left), -100, os.fsencode(right), 2)
    if result != 0:
        error = ctypes.get_errno()
        raise GateError(f"atomic_exchange_failed: {errno.errorcode.get(error, error)}")


def publish_payload_directory_atomically(
    candidate_payload: Path,
    target_payload: Path,
    *,
    exchange: Callable[[Path, Path], None] | None = None,
    fail_before_exchange: bool = False,
) -> None:
    candidate = Path(candidate_payload)
    target = Path(target_payload)
    if (
        not candidate.is_dir()
        or candidate.is_symlink()
        or not target.is_dir()
        or target.is_symlink()
    ):
        raise GateError("publication_directory")
    candidate_files = [path for path in sorted(candidate.rglob("*")) if path.is_file()]
    if not candidate_files or any(path.is_symlink() for path in candidate_files):
        raise GateError("publication_candidate")
    staging = Path(tempfile.mkdtemp(prefix=".supplemental-r3-a03-publish-", dir=target.parent))
    exchanged = False
    try:
        staging.rmdir()
        shutil.copytree(target, staging, symlinks=True)
        for source in candidate_files:
            relative = source.relative_to(candidate)
            destination = staging / relative
            if destination.exists() or destination.is_symlink():
                raise GateError(f"publication_target: {relative.as_posix()}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            _common.atomic_write_bytes(destination, source.read_bytes())
        if fail_before_exchange:
            raise OSError("synthetic publication failure")
        (exchange or _atomic_exchange_directories)(target, staging)
        exchanged = True
        for source in candidate_files:
            relative = source.relative_to(candidate)
            published = target / relative
            if (
                not published.is_file()
                or published.is_symlink()
                or published.read_bytes() != source.read_bytes()
            ):
                raise GateError(f"publication_incomplete: {relative.as_posix()}")
        shutil.rmtree(staging)
    except Exception as exc:
        if not exchanged and staging.is_dir() and not staging.is_symlink():
            shutil.rmtree(staging)
        if isinstance(exc, GateError):
            raise
        raise GateError(f"publication_failed: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build-payload", "verify-payload", "publish-payload"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--candidate-root", type=Path, required=True)
        command.add_argument("--authority", required=True)
        command.add_argument("--journal", type=Path, required=True)
        command.add_argument("--branch", required=True)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    handlers: dict[str, Callable[..., int]] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    active = handlers or {
        "build-payload": handle_build_payload,
        "verify-payload": handle_verify_payload,
        "publish-payload": handle_publish_payload,
    }
    values = vars(args).copy()
    command = values.pop("command")
    try:
        return int(active[command](**values))
    except Exception as exc:
        if handlers is None and isinstance(values.get("journal"), Path) and values["journal"].is_file():
            _common.persist_cli_failure(values["journal"], f"admission_{command}", exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
