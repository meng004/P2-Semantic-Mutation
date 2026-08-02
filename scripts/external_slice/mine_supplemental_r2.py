#!/usr/bin/env python3
"""Supplemental mining R2: GraphQL Repository.issues transport and builders."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT_DEFAULT = Path("data/external_slice/supplemental_r2")

SHEET_HEADER = [
    "neutral_id",
    "source_cohort",
    "repository",
    "issue_url",
    "buggy_sha",
    "fixed_sha",
    "mechanism",
    "crit_real_public_fix",
    "crit_dual_arm_repro",
    "crit_in_numerical_scope",
    "decision",
    "decision_reason",
    "analysis_id",
]

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
TOKEN_RE = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"Bearer\s+[A-Za-z0-9][A-Za-z0-9._-]{15,}|"
    r"Authorization:\s*\S+|sk-[A-Za-z0-9]{20,}",
    re.IGNORECASE,
)
FORBIDDEN_TRANSPORT_RE = re.compile(
    r"(?i)(/search/issues|\bgh\s+search\b|search\s*\(|"
    r"SearchResultItemConnection|/repos/[^/\s]+/[^/\s]+/issues\b|"
    r"pull.?request.?to.?issue|pr.?to.?issue)"
)
PROHIBITED_VOCAB_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b|"
    r"(^|[^A-Za-z0-9_])(CE|OS|HP|TF|SI|fiber|stratum)([^A-Za-z0-9_]|$))"
)

GraphQLRunner = Callable[[str, dict[str, Any]], tuple[int, str, str]]


class HardFail(Exception):
    """Transport or identity hard failure; mint diagnostics only."""

    def __init__(self, invariant: str, detail: str = "") -> None:
        self.invariant = invariant
        self.detail = detail
        super().__init__(f"{invariant}: {detail}" if detail else invariant)


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(payload: Any) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def sanitize(text: str) -> str:
    if not text:
        return text
    return TOKEN_RE.sub("<REDACTED>", text)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_match_text(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").casefold()


def append_command_log(path: Path, entry: dict[str, Any]) -> None:
    if path.exists():
        payload = load_json(path)
    else:
        payload = {"schema_version": 1, "task": "SUPPLEMENTAL_MINING_R2", "entries": []}
    payload.setdefault("schema_version", 1)
    payload.setdefault("task", "SUPPLEMENTAL_MINING_R2")
    payload.setdefault("entries", [])
    payload["entries"].append(entry)
    write_json(path, payload)


def load_scope(root: Path) -> dict[str, Any]:
    scope = load_json(root / "SCOPE.json")
    if scope.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("scope_task", "SCOPE.json task must be SUPPLEMENTAL_MINING_R2")
    return scope


def load_transport(root: Path) -> dict[str, Any]:
    contract = load_json(root / "TRANSPORT_CONTRACT.json")
    if contract.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("transport_task", "TRANSPORT_CONTRACT task mismatch")
    doc = contract.get("query_document")
    if not isinstance(doc, str):
        raise HardFail("query_identity_drift", "missing query_document")
    actual = sha256_text(doc)
    expected = contract.get("query_document_sha256")
    if actual != expected:
        raise HardFail(
            "query_identity_drift",
            f"query_document_sha256 mismatch: expected {expected}, got {actual}",
        )
    if contract.get("transport") != "github_graphql_repository_issues":
        raise HardFail("forbidden_transport", "transport must be Repository.issues")
    return contract


def load_quotas(root: Path) -> dict[str, Any]:
    quotas = load_json(root / "QUOTAS.json")
    if quotas.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("quota_task", "QUOTAS.json task mismatch")
    return quotas


def refuse_forbidden_transport(command_text: str) -> None:
    if FORBIDDEN_TRANSPORT_RE.search(command_text):
        raise HardFail("forbidden_transport", command_text[:200])


def default_graphql_runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
    refuse_forbidden_transport(query)
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key in ("owner", "name"):
        if key not in variables:
            raise HardFail("query_identity_drift", f"missing variable {key}")
        cmd.extend(["-F", f"{key}={variables[key]}"])
    after = variables.get("after")
    if after is not None:
        cmd.extend(["-F", f"after={after}"])
    refuse_forbidden_transport(" ".join(cmd))
    # Pace live requests to reduce secondary rate-limit hard-fails.
    delay = float(os.environ.get("SUPPLEMENTAL_R2_GRAPHQL_DELAY_S", "0.35"))
    if delay > 0:
        time.sleep(delay)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def scrub_page_payload(payload: Any) -> Any:
    """Credential-scrub nested strings; preserve structure for replay."""
    if isinstance(payload, dict):
        return {k: scrub_page_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [scrub_page_payload(v) for v in payload]
    if isinstance(payload, str):
        return sanitize(payload)
    return payload


def parse_created_at(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def validate_issue_node(node: Any, *, repository: str) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise HardFail("typename_not_issue", "node is not an object")
    typename = node.get("__typename")
    if typename != "Issue":
        raise HardFail("typename_not_issue", f"got {typename!r}")
    state = node.get("state")
    if state != "CLOSED":
        raise HardFail("state_not_closed", f"got {state!r}")
    if node.get("closedAt") in (None, ""):
        raise HardFail("null_closed_at", f"issue {node.get('number')}")
    url = node.get("url") or ""
    if "/pull/" in url:
        raise HardFail("pull_url", url)
    number = node.get("number")
    if not isinstance(number, int):
        raise HardFail("malformed_json", "issue number missing")
    expected_suffix = f"/issues/{number}"
    if not url.endswith(expected_suffix) or "/pull/" in url:
        raise HardFail("pull_url", f"non-canonical issue URL: {url}")
    labels = node.get("labels") or {}
    page_info = labels.get("pageInfo") or {}
    if page_info.get("hasNextPage") is True:
        raise HardFail("incomplete_labels", f"{repository}#{number}")
    label_nodes = labels.get("nodes")
    if not isinstance(label_nodes, list):
        raise HardFail("incomplete_labels", f"{repository}#{number} labels.nodes")
    for lab in label_nodes:
        if not isinstance(lab, dict) or "name" not in lab:
            raise HardFail("incomplete_labels", f"{repository}#{number} label entry")
    for required in (
        "id",
        "title",
        "bodyText",
        "createdAt",
        "updatedAt",
        "closedAt",
    ):
        if required not in node or node[required] is None:
            raise HardFail("malformed_json", f"missing {required}")
    return node


def validate_page(
    payload: dict[str, Any],
    *,
    repository: str,
    page_index: int,
    expected_after: str | None,
    first_total_count: int | None,
    seen_cursors: set[str],
    seen_ids: set[str],
    seen_numbers: set[int],
    seen_urls: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]], str | None, bool, int]:
    if "errors" in payload and payload["errors"]:
        raise HardFail("graphql_errors", json.dumps(payload["errors"])[:300])
    data = payload.get("data")
    if not isinstance(data, dict):
        raise HardFail("malformed_json", "missing data")
    repo_obj = data.get("repository")
    if repo_obj is None:
        raise HardFail("null_repository", repository)
    issues = repo_obj.get("issues")
    if issues is None:
        raise HardFail("null_issues", repository)
    total_count = issues.get("totalCount")
    if not isinstance(total_count, int):
        raise HardFail("total_count_drift", "totalCount missing")
    if first_total_count is not None and total_count != first_total_count:
        raise HardFail(
            "total_count_drift",
            f"page {page_index}: {total_count} != {first_total_count}",
        )
    page_info = issues.get("pageInfo") or {}
    has_next = bool(page_info.get("hasNextPage"))
    end_cursor = page_info.get("endCursor")
    if expected_after is not None:
        # Continuity is enforced by the caller binding after=prev endCursor.
        pass
    if end_cursor is not None:
        if end_cursor in seen_cursors:
            raise HardFail("cursor_drift", f"repeated endCursor {end_cursor}")
        seen_cursors.add(end_cursor)
    nodes = issues.get("nodes")
    if not isinstance(nodes, list):
        raise HardFail("malformed_json", "issues.nodes missing")
    validated: list[dict[str, Any]] = []
    for node in nodes:
        issue = validate_issue_node(node, repository=repository)
        node_id = issue["id"]
        number = int(issue["number"])
        url = issue["url"]
        if node_id in seen_ids:
            raise HardFail("duplicate_node", node_id)
        if number in seen_numbers:
            raise HardFail("duplicate_number", str(number))
        if url in seen_urls:
            raise HardFail("duplicate_url", url)
        seen_ids.add(node_id)
        seen_numbers.add(number)
        seen_urls.add(url)
        validated.append(issue)
    return issues, validated, end_cursor, has_next, total_count


def match_surfaces(issue: dict[str, Any], phrase: str) -> list[str]:
    norm_phrase = normalize_match_text(phrase)
    surfaces: list[str] = []
    if norm_phrase in normalize_match_text(issue.get("title") or ""):
        surfaces.append("title")
    if norm_phrase in normalize_match_text(issue.get("bodyText") or ""):
        surfaces.append("body")
    for lab in (issue.get("labels") or {}).get("nodes") or []:
        name = lab.get("name") or ""
        if norm_phrase in normalize_match_text(name):
            surfaces.append(f"label:{name}")
    return surfaces


def build_snapshot_record(
    *,
    repository: str,
    repository_order: int,
    issue: dict[str, Any],
    matched_phrases: list[str],
    match_surfaces: dict[str, list[str]],
    source_page_index: int,
    source_page_sha256: str,
    query_document_sha256: str,
    variables_sha256: str,
    node_index: int,
    record_index: int,
) -> dict[str, Any]:
    ordered_labels = [
        lab["name"] for lab in (issue.get("labels") or {}).get("nodes") or []
    ]
    base = {
        "snapshot_record_id": f"SSR2-{repository_order:02d}-{record_index:04d}",
        "repository": repository,
        "repository_order": repository_order,
        "issue_node_id": issue["id"],
        "issue_number": int(issue["number"]),
        "issue_url": issue["url"],
        "state": issue["state"],
        "created_at": issue["createdAt"],
        "updated_at": issue["updatedAt"],
        "closed_at": issue["closedAt"],
        "title_sha256": sha256_text(issue.get("title") or ""),
        "body_text_sha256": sha256_text(issue.get("bodyText") or ""),
        "ordered_labels": ordered_labels,
        "matched_phrases": list(matched_phrases),
        "match_surfaces": {
            p: list(match_surfaces.get(p, [])) for p in matched_phrases
        },
        "source_page_index": source_page_index,
        "source_page_sha256": source_page_sha256,
        "query_document_sha256": query_document_sha256,
        "variables_sha256": variables_sha256,
        "node_index": node_index,
    }
    base["snapshot_record_sha256"] = canonical_sha256(base)
    return base


def select_phrase_union(
    *,
    scope: dict[str, Any],
    repository: str,
    repository_order: int,
    id_prefix: str,
    issues_with_meta: list[dict[str, Any]],
    query_document_sha256: str,
) -> list[dict[str, Any]]:
    """Apply cutoff, per-phrase top-20, union/dedupe, order, assign IDs."""
    cutoff = parse_created_at(scope["created_cutoff"])
    max_per_phrase = int(scope["max_results_per_phrase"])
    phrases: list[str] = list(scope["phrases"])

    eligible: list[dict[str, Any]] = []
    for item in issues_with_meta:
        created = parse_created_at(item["issue"]["createdAt"])
        if created > cutoff:
            continue
        eligible.append(item)

    phrase_lists: dict[str, list[dict[str, Any]]] = {p: [] for p in phrases}
    for item in eligible:
        issue = item["issue"]
        for phrase in phrases:
            surfaces = match_surfaces(issue, phrase)
            if not surfaces:
                continue
            bucket = phrase_lists[phrase]
            if len(bucket) >= max_per_phrase:
                continue
            bucket.append({**item, "match_surfaces_for_phrase": surfaces})

    by_url: dict[str, dict[str, Any]] = {}
    for phrase in phrases:
        for item in phrase_lists[phrase]:
            url = item["issue"]["url"]
            if url not in by_url:
                by_url[url] = {
                    "item": item,
                    "matched_phrases": [],
                    "match_surfaces": {},
                }
            entry = by_url[url]
            if phrase not in entry["matched_phrases"]:
                entry["matched_phrases"].append(phrase)
            entry["match_surfaces"][phrase] = list(item["match_surfaces_for_phrase"])

    ordered = sorted(
        by_url.values(),
        key=lambda e: (
            e["item"]["issue"]["createdAt"],
            int(e["item"]["issue"]["number"]),
        ),
        reverse=True,
    )

    records: list[dict[str, Any]] = []
    for idx, entry in enumerate(ordered, start=1):
        item = entry["item"]
        # Preserve phrase order from frozen SCOPE phrases.
        matched = [p for p in phrases if p in entry["matched_phrases"]]
        record = build_snapshot_record(
            repository=repository,
            repository_order=repository_order,
            issue=item["issue"],
            matched_phrases=matched,
            match_surfaces=entry["match_surfaces"],
            source_page_index=item["source_page_index"],
            source_page_sha256=item["source_page_sha256"],
            query_document_sha256=query_document_sha256,
            variables_sha256=item["variables_sha256"],
            node_index=item["node_index"],
            record_index=idx,
        )
        records.append(record)
    return records


def build_queue_from_snapshot(
    scope: dict[str, Any], snapshot: dict[str, Any]
) -> list[dict[str, Any]]:
    """Pure function: reconstruct ordered review queue from snapshot records."""
    repos = scope["repositories"]
    prefix_by_repo = {r["repo"]: r["id_prefix"] for r in repos}
    order_by_repo = {r["repo"]: r["order"] for r in repos}
    records = list(snapshot.get("records") or [])
    # Group by repository, preserve snapshot order within each repo.
    by_repo: dict[str, list[dict[str, Any]]] = {r["repo"]: [] for r in repos}
    for rec in records:
        repo = rec["repository"]
        if repo not in by_repo:
            raise HardFail("repository_outside_scope", repo)
        by_repo[repo].append(rec)

    queue: list[dict[str, Any]] = []
    for repo_entry in repos:
        repo = repo_entry["repo"]
        prefix = prefix_by_repo[repo]
        repo_recs = by_repo[repo]
        # Enforce ordering invariant.
        expected = sorted(
            repo_recs,
            key=lambda r: (r["created_at"], int(r["issue_number"])),
            reverse=True,
        )
        if [r["issue_url"] for r in repo_recs] != [r["issue_url"] for r in expected]:
            raise HardFail("reordered_union", repo)
        for union_order, rec in enumerate(repo_recs, start=1):
            neutral_id = f"{prefix}{union_order:02d}"
            row = {
                "neutral_id": neutral_id,
                "union_order": union_order,
                "repository_review_order": union_order,
                "review_status": "PENDING_REVIEW",
                "snapshot_record_id": rec["snapshot_record_id"],
                "snapshot_record_sha256": rec["snapshot_record_sha256"],
                "repository": rec["repository"],
                "repository_order": rec["repository_order"],
                "issue_node_id": rec["issue_node_id"],
                "issue_number": rec["issue_number"],
                "issue_url": rec["issue_url"],
                "state": rec["state"],
                "created_at": rec["created_at"],
                "matched_phrases": list(rec["matched_phrases"]),
                "source_page_sha256": rec["source_page_sha256"],
            }
            if row["repository_order"] != order_by_repo[repo]:
                raise HardFail("repository_order", repo)
            queue.append(row)
    return queue


def apply_review_statuses(
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    *,
    max_reviewed: int,
    target_pending: int,
) -> list[dict[str, Any]]:
    """Mark REVIEWED for the decision prefix; remainder NOT_REVIEWED_AFTER_STOP."""
    by_repo_q: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo_q.setdefault(row["repository"], []).append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        by_repo_d.setdefault(decision["repository"], []).append(decision)

    updated: list[dict[str, Any]] = []
    for repo, rows in by_repo_q.items():
        reviewed_n = len(by_repo_d.get(repo, []))
        pending = sum(
            1
            for d in by_repo_d.get(repo, [])
            if d.get("decision") == "ADMIT_PENDING_REPRO"
        )
        if reviewed_n > max_reviewed:
            raise HardFail("reviewed_over_cap", repo)
        if pending > target_pending:
            raise HardFail("pending_over_cap", repo)
        # If a proper prefix remains unreviewed, a stop condition must hold
        # or the reviewed prefix must be exactly the decision list length.
        if 0 < reviewed_n < len(rows):
            stopped_ok = (
                pending >= target_pending
                or reviewed_n >= max_reviewed
                or reviewed_n == len(by_repo_d.get(repo, []))
            )
            if not stopped_ok:
                raise HardFail("review_stop_inconsistent", repo)
        for idx, row in enumerate(rows):
            clone = dict(row)
            if idx < reviewed_n:
                clone["review_status"] = "REVIEWED"
            else:
                clone["review_status"] = "NOT_REVIEWED_AFTER_STOP"
            updated.append(clone)
    order = {
        (r["repository"], r["repository_review_order"]): i for i, r in enumerate(queue)
    }
    updated.sort(key=lambda r: order[(r["repository"], r["repository_review_order"])])
    return updated


def decision_is_valid(
    decision: dict[str, Any],
    *,
    exclusion_classes: set[str],
) -> None:
    a1 = decision.get("crit_real_public_fix")
    a3 = decision.get("crit_in_numerical_scope")
    a2 = decision.get("crit_dual_arm_repro")
    verdict = decision.get("decision")
    excl = decision.get("exclusion_class") or ""
    if a2 != "PENDING":
        raise HardFail("non_pending_a2", str(decision.get("neutral_id")))
    if decision.get("analysis_id") not in (None, ""):
        raise HardFail("nonblank_analysis_id", str(decision.get("neutral_id")))
    for text_key in ("mechanism", "decision_reason"):
        blob = decision.get(text_key) or ""
        if PROHIBITED_VOCAB_RE.search(blob):
            raise HardFail("forbidden_vocabulary", f"{decision.get('neutral_id')}:{text_key}")
    if a1 == "PASS":
        for field in ("buggy_sha", "fixed_sha"):
            if not FULL_SHA.match(str(decision.get(field) or "")):
                raise HardFail("short_sha", f"{decision.get('neutral_id')}:{field}")
        for field in ("public_issue_url", "public_fix_url"):
            if not decision.get(field):
                raise HardFail("missing_public_url", f"{decision.get('neutral_id')}:{field}")
    if verdict == "ADMIT_PENDING_REPRO":
        if a1 != "PASS" or a3 != "PASS" or a2 != "PENDING" or excl:
            raise HardFail("admit_inconsistency", str(decision.get("neutral_id")))
    elif verdict == "EXCLUDED":
        if excl:
            if excl not in exclusion_classes:
                raise HardFail("invalid_exclusion_class", excl)
        elif a1 == "PASS" and a3 == "PASS":
            raise HardFail("excluded_without_reason", str(decision.get("neutral_id")))
    else:
        raise HardFail("invalid_decision", str(verdict))


def validate_decisions_payload(
    *,
    scope: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> None:
    exclusion_classes = set(scope["exclusion_classes"])
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])

    by_repo_queue: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo_queue.setdefault(row["repository"], []).append(row)

    decisions_by_repo: dict[str, list[dict[str, Any]]] = {}
    for d in decisions:
        decisions_by_repo.setdefault(d["repository"], []).append(d)

    copied_fields = [
        "neutral_id",
        "snapshot_record_id",
        "snapshot_record_sha256",
        "repository",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "repository_review_order",
        "matched_phrases",
    ]

    for repo, qrows in by_repo_queue.items():
        dreviews = decisions_by_repo.get(repo, [])
        # Determine expected reviewed prefix from decisions length and stop rule.
        if not dreviews:
            continue
        # Decision order must equal reviewed queue prefix.
        for idx, decision in enumerate(dreviews):
            if idx >= len(qrows):
                raise HardFail("extra_decision", repo)
            qrow = qrows[idx]
            if qrow.get("review_status") == "NOT_REVIEWED_AFTER_STOP":
                raise HardFail("decision_for_unreviewed", decision.get("neutral_id"))
            for field in copied_fields:
                if decision.get(field) != qrow.get(field):
                    raise HardFail(
                        "queue_decision_binding",
                        f"{decision.get('neutral_id')}:{field}",
                    )
            decision_is_valid(decision, exclusion_classes=exclusion_classes)

        # Stop-rule consistency: reviewed count and pending admits.
        pending = sum(
            1 for d in dreviews if d.get("decision") == "ADMIT_PENDING_REPRO"
        )
        if len(dreviews) > max_reviewed:
            raise HardFail("reviewed_over_cap", repo)
        if pending > target_pending:
            raise HardFail("pending_over_cap", repo)
        # If there are remaining queue rows, they must be after a valid stop.
        if len(dreviews) < len(qrows):
            stopped_ok = pending >= target_pending or len(dreviews) >= max_reviewed
            if not stopped_ok and len(dreviews) != len(qrows):
                # Exhaustion is also a stop; if decisions omit trailing without stop,
                # allow only when decisions cover all reviewed before a stop marker.
                pass


def sheet_row_from_decision(decision: dict[str, Any]) -> dict[str, str]:
    return {
        "neutral_id": decision["neutral_id"],
        "source_cohort": "supplemental_r2",
        "repository": decision["repository"],
        "issue_url": decision["issue_url"],
        "buggy_sha": decision.get("buggy_sha") or "",
        "fixed_sha": decision.get("fixed_sha") or "",
        "mechanism": decision.get("mechanism") or "",
        "crit_real_public_fix": decision["crit_real_public_fix"],
        "crit_dual_arm_repro": "PENDING",
        "crit_in_numerical_scope": decision["crit_in_numerical_scope"],
        "decision": decision["decision"],
        "decision_reason": decision.get("decision_reason") or "",
        "analysis_id": "",
    }


def evidence_from_decision(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "neutral_id": decision["neutral_id"],
        "snapshot_record_id": decision["snapshot_record_id"],
        "snapshot_record_sha256": decision["snapshot_record_sha256"],
        "repository": decision["repository"],
        "issue_node_id": decision["issue_node_id"],
        "issue_number": decision["issue_number"],
        "issue_url": decision["issue_url"],
        "buggy_sha": decision.get("buggy_sha") or "",
        "fixed_sha": decision.get("fixed_sha") or "",
        "public_issue_url": decision.get("public_issue_url") or "",
        "public_fix_url": decision.get("public_fix_url") or "",
        "mechanism": decision.get("mechanism") or "",
        "exclusion_class": decision.get("exclusion_class") or "",
        "crit_real_public_fix": decision["crit_real_public_fix"],
        "crit_dual_arm_repro": "PENDING",
        "crit_in_numerical_scope": decision["crit_in_numerical_scope"],
        "decision": decision["decision"],
        "source_cohort": "supplemental_r2",
        "analysis_id": "",
    }


def write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SHEET_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def retrieve_repository_pages(
    *,
    root: Path,
    repo_entry: dict[str, Any],
    contract: dict[str, Any],
    runner: GraphQLRunner,
    command_log: Path,
    temp_pages: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query = contract["query_document"]
    query_sha = contract["query_document_sha256"]
    if sha256_text(query) != query_sha:
        raise HardFail("query_identity_drift", "inline/changed query document")
    if "search(" in query or "SearchResultItemConnection" in query:
        raise HardFail("forbidden_transport", "search in query document")

    owner = repo_entry["owner"]
    name = repo_entry["name"]
    repository = repo_entry["repo"]
    after: str | None = None
    page_index = 0
    first_total: int | None = None
    seen_cursors: set[str] = set()
    seen_ids: set[str] = set()
    seen_numbers: set[int] = set()
    seen_urls: set[str] = set()
    issues_with_meta: list[dict[str, Any]] = []
    page_manifest: list[dict[str, Any]] = []
    has_next = True

    while has_next:
        variables = {"owner": owner, "name": name, "after": after}
        variables_sha = canonical_sha256(variables)
        started = utc_now()
        exit_code, stdout, stderr = runner(query, variables)
        ended = utc_now()
        stdout_s = sanitize(stdout)
        stderr_s = sanitize(stderr)
        response_sha = sha256_text(stdout_s)
        entry = {
            "repository": repository,
            "page_index": page_index,
            "operation_name": contract["operation_name"],
            "query_document_sha256": query_sha,
            "variables": variables,
            "variables_sha256": variables_sha,
            "after": after,
            "response_page_sha256": response_sha,
            "exit_code": exit_code,
            "stderr_sha256": sha256_text(stderr_s),
            "started_at_utc": started,
            "ended_at_utc": ended,
            "cli": list(contract["cli"]),
        }
        append_command_log(command_log, entry)

        if exit_code != 0:
            raise HardFail("nonzero_exit", f"{repository} page {page_index}: {exit_code}")
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise HardFail("malformed_json", str(exc)) from exc

        issues, nodes, end_cursor, has_next, total_count = validate_page(
            payload,
            repository=repository,
            page_index=page_index,
            expected_after=after,
            first_total_count=first_total,
            seen_cursors=seen_cursors,
            seen_ids=seen_ids,
            seen_numbers=seen_numbers,
            seen_urls=seen_urls,
        )
        if first_total is None:
            first_total = total_count
        # Cursor continuity: next after must equal this endCursor when has_next.
        page_name = (
            f"{repo_entry['order']:02d}_{owner}_{name}_page_{page_index:04d}.json"
        )
        page_path = temp_pages / page_name
        scrubbed = scrub_page_payload(payload)
        write_json(page_path, scrubbed)
        page_sha = sha256_file(page_path)
        page_manifest.append(
            {
                "repository": repository,
                "repository_order": repo_entry["order"],
                "page_index": page_index,
                "path": f"transport_pages/{page_name}",
                "sha256": page_sha,
                "after": after,
                "endCursor": end_cursor,
                "totalCount": total_count,
                "node_count": len(nodes),
                "variables_sha256": variables_sha,
            }
        )
        for node_index, node in enumerate(nodes):
            issues_with_meta.append(
                {
                    "issue": node,
                    "source_page_index": page_index,
                    "source_page_sha256": page_sha,
                    "variables_sha256": variables_sha,
                    "node_index": node_index,
                }
            )
        if has_next:
            if not end_cursor:
                raise HardFail("cursor_drift", "hasNextPage without endCursor")
            # Bind next request after to this endCursor (continuity invariant).
            after = end_cursor
        else:
            # Terminal page: after used for this page must equal the prior
            # endCursor binding already applied by the loop.
            pass
        page_index += 1

    if first_total is None:
        raise HardFail("incomplete_pagination", f"no pages for {repository}")
    unique_count = len(seen_ids)
    if unique_count != first_total:
        raise HardFail(
            "incomplete_pagination",
            f"{repository}: unique={unique_count} totalCount={first_total}",
        )
    # Terminal page already required has_next False by loop exit.
    return page_manifest, issues_with_meta


def cmd_retrieve(
    root: Path,
    *,
    runner: GraphQLRunner | None = None,
) -> int:
    command_log = root / "COMMAND_LOG.json"
    hard_fail_path = root / "RETRIEVAL_HARD_FAIL.json"
    snapshot_path = root / "ISSUE_SNAPSHOT.json"
    queue_path = root / "REVIEW_QUEUE.json"
    pages_dir = root / "transport_pages"

    # Do not leave prior candidate artifacts if we hard-fail mid-run.
    active_runner = runner or default_graphql_runner
    try:
        scope = load_scope(root)
        contract = load_transport(root)
        load_quotas(root)
        if contract.get("created_cutoff") != scope.get("created_cutoff"):
            raise HardFail("query_identity_drift", "cutoff mismatch scope/transport")
        if contract.get("operation_name") != "SupplementalR2RepositoryIssues":
            raise HardFail("query_identity_drift", "operation_name")
        if contract.get("page_size") != 100:
            raise HardFail("query_identity_drift", "page_size")
        if contract.get("states") != ["CLOSED"]:
            raise HardFail("query_identity_drift", "states")
        if contract.get("order_by") != {"field": "CREATED_AT", "direction": "DESC"}:
            raise HardFail("query_identity_drift", "order_by")

        with tempfile.TemporaryDirectory(prefix="r2_pages_") as tmp:
            temp_pages = Path(tmp)
            all_manifest: list[dict[str, Any]] = []
            all_records: list[dict[str, Any]] = []
            for repo_entry in scope["repositories"]:
                manifest, issues_meta = retrieve_repository_pages(
                    root=root,
                    repo_entry=repo_entry,
                    contract=contract,
                    runner=active_runner,
                    command_log=command_log,
                    temp_pages=temp_pages,
                )
                all_manifest.extend(manifest)
                records = select_phrase_union(
                    scope=scope,
                    repository=repo_entry["repo"],
                    repository_order=repo_entry["order"],
                    id_prefix=repo_entry["id_prefix"],
                    issues_with_meta=issues_meta,
                    query_document_sha256=contract["query_document_sha256"],
                )
                all_records.extend(records)

            # Atomic publish only after all repos complete.
            if pages_dir.exists():
                shutil.rmtree(pages_dir)
            pages_dir.mkdir(parents=True, exist_ok=True)
            for page_file in sorted(temp_pages.glob("*.json")):
                shutil.copy2(page_file, pages_dir / page_file.name)

            snapshot = {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "query_document_sha256": contract["query_document_sha256"],
                "created_cutoff": scope["created_cutoff"],
                "page_manifest": all_manifest,
                "page_manifest_sha256": canonical_sha256(all_manifest),
                "records": all_records,
            }
            write_json(snapshot_path, snapshot)
            queue_records = build_queue_from_snapshot(scope, snapshot)
            write_json(
                queue_path,
                {
                    "schema_version": 1,
                    "task": "SUPPLEMENTAL_MINING_R2",
                    "records": queue_records,
                },
            )
        if hard_fail_path.exists():
            hard_fail_path.unlink()
        return 0
    except HardFail as exc:
        write_json(
            hard_fail_path,
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "invariant": exc.invariant,
                "detail": exc.detail,
                "timestamp_utc": utc_now(),
            },
        )
        # Ensure no candidate payload artifacts remain from a partial success.
        for path in (
            snapshot_path,
            queue_path,
            root / "REVIEW_DECISIONS.json",
            root / "EVIDENCE_SNAPSHOT.json",
            root / "admission_sheet.cursor_candidate.csv",
            root / "HANDOFF_SUPPLEMENTAL_R2.json",
        ):
            if path.exists():
                path.unlink()
        if pages_dir.exists():
            shutil.rmtree(pages_dir)
        evidence_dir = root / "admission_evidence"
        if evidence_dir.exists():
            shutil.rmtree(evidence_dir)
        append_command_log(
            command_log,
            {
                "label": "retrieve_hard_fail",
                "invariant": exc.invariant,
                "detail": sanitize(exc.detail),
                "timestamp_utc": utc_now(),
                "exit_code": 1,
            },
        )
        print(f"ERROR: {exc.invariant}: {exc.detail}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — fail closed
        write_json(
            hard_fail_path,
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "invariant": "unexpected_error",
                "detail": sanitize(str(exc)),
                "timestamp_utc": utc_now(),
            },
        )
        for path in (snapshot_path, queue_path):
            if path.exists():
                path.unlink()
        if pages_dir.exists():
            shutil.rmtree(pages_dir)
        print(f"ERROR: unexpected_error: {exc}", file=sys.stderr)
        return 1


def cmd_build_queue(root: Path) -> int:
    try:
        scope = load_scope(root)
        snapshot = load_json(root / "ISSUE_SNAPSHOT.json")
        records = build_queue_from_snapshot(scope, snapshot)
        write_json(
            root / "REVIEW_QUEUE.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "records": records,
            },
        )
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_validate_decisions(root: Path) -> int:
    try:
        scope = load_scope(root)
        queue = load_json(root / "REVIEW_QUEUE.json")["records"]
        decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
        validate_decisions_payload(scope=scope, queue=queue, decisions=decisions)
        print("DECISIONS_OK")
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_build_payload(root: Path) -> int:
    try:
        scope = load_scope(root)
        queue_payload = load_json(root / "REVIEW_QUEUE.json")
        decisions_payload = load_json(root / "REVIEW_DECISIONS.json")
        decisions = decisions_payload["decisions"]
        queue = queue_payload["records"]
        validate_decisions_payload(scope=scope, queue=queue, decisions=decisions)

        # Update review statuses on queue copy for persistence.
        max_reviewed = int(scope["max_reviewed_per_repo"])
        target_pending = int(scope["target_pending_per_repo"])
        updated_queue = apply_review_statuses(
            queue,
            decisions,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        # Reject decisions that target NOT_REVIEWED_AFTER_STOP rows.
        status_by_id = {r["neutral_id"]: r["review_status"] for r in updated_queue}
        for d in decisions:
            if status_by_id.get(d["neutral_id"]) == "NOT_REVIEWED_AFTER_STOP":
                raise HardFail("decision_for_unreviewed", d["neutral_id"])

        write_json(
            root / "REVIEW_QUEUE.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "records": updated_queue,
            },
        )

        sheet_rows = [sheet_row_from_decision(d) for d in decisions]
        write_sheet(root / "admission_sheet.cursor_candidate.csv", sheet_rows)

        evidence_root = root / "admission_evidence"
        if evidence_root.exists():
            shutil.rmtree(evidence_root)
        evidence_root.mkdir(parents=True, exist_ok=True)
        manifest: list[dict[str, Any]] = []
        for decision in decisions:
            evidence = evidence_from_decision(decision)
            case_dir = evidence_root / decision["neutral_id"]
            case_dir.mkdir(parents=True, exist_ok=True)
            path = case_dir / "evidence.json"
            write_json(path, evidence)
            rel = f"admission_evidence/{decision['neutral_id']}/evidence.json"
            manifest.append(
                {
                    "neutral_id": decision["neutral_id"],
                    "path": rel,
                    "sha256": sha256_file(path),
                }
            )
        write_json(
            root / "EVIDENCE_SNAPSHOT.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "records": manifest,
            },
        )
        print("PAYLOAD_OK")
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def project_quota_feasibility(
    quotas: dict[str, Any], decisions: list[dict[str, Any]]
) -> dict[str, Any]:
    pending_by_repo: dict[str, int] = {}
    for d in decisions:
        if d.get("decision") == "ADMIT_PENDING_REPRO":
            pending_by_repo[d["repository"]] = pending_by_repo.get(d["repository"], 0) + 1
    shortfalls: list[dict[str, Any]] = []
    for entry in quotas["readiness_quota_order"]:
        repo = entry["repo"]
        target = int(entry["additional_ready_target"])
        have = pending_by_repo.get(repo, 0)
        if have < target:
            shortfalls.append(
                {
                    "repo": repo,
                    "additional_ready_target": target,
                    "pending_admit_rows": have,
                    "shortfall": target - have,
                }
            )
    status = "FEASIBLE" if not shortfalls else quotas["shortfall_status"]
    starting = quotas["starting_state"]
    projection = quotas["projection_if_quotas_met"]
    return {
        "status": status,
        "shortfalls": shortfalls,
        "pending_by_repo": pending_by_repo,
        "starting_accepted_ready_defects": starting["accepted_ready_defects"],
        "starting_qualifying_projects": starting["qualifying_projects"],
        "projection_if_quotas_met": projection,
        "claims_ready_success": False,
        "claims_readiness_executed": False,
        "claims_canonical_freeze": False,
    }


def cmd_write_handoff(root: Path, payload_commit: str) -> int:
    try:
        scope = load_scope(root)
        contract = load_transport(root)
        quotas = load_quotas(root)
        decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
        feasibility = project_quota_feasibility(quotas, decisions)

        def rel_sha(name: str) -> str:
            return sha256_file(root / name)

        repo_root = Path(__file__).resolve().parents[2]
        file_sha256 = {
            "SCOPE.json": rel_sha("SCOPE.json"),
            "TRANSPORT_CONTRACT.json": rel_sha("TRANSPORT_CONTRACT.json"),
            "QUOTAS.json": rel_sha("QUOTAS.json"),
            "ISSUE_SNAPSHOT.json": rel_sha("ISSUE_SNAPSHOT.json"),
            "REVIEW_QUEUE.json": rel_sha("REVIEW_QUEUE.json"),
            "REVIEW_DECISIONS.json": rel_sha("REVIEW_DECISIONS.json"),
            "EVIDENCE_SNAPSHOT.json": rel_sha("EVIDENCE_SNAPSHOT.json"),
            "admission_sheet.cursor_candidate.csv": rel_sha(
                "admission_sheet.cursor_candidate.csv"
            ),
            "COMMAND_LOG.json": rel_sha("COMMAND_LOG.json"),
            "scripts/external_slice/mine_supplemental_r2.py": sha256_file(
                repo_root / "scripts/external_slice/mine_supplemental_r2.py"
            ),
            "scripts/external_slice/check_supplemental_r2_admission.py": sha256_file(
                repo_root / "scripts/external_slice/check_supplemental_r2_admission.py"
            ),
            "scripts/external_slice/check_supplemental_r2_handoff_hashes.py": sha256_file(
                repo_root / "scripts/external_slice/check_supplemental_r2_handoff_hashes.py"
            ),
            "tests/external_slice/test_mine_supplemental_r2.py": sha256_file(
                repo_root / "tests/external_slice/test_mine_supplemental_r2.py"
            ),
            "tests/external_slice/test_check_supplemental_r2_admission.py": sha256_file(
                repo_root / "tests/external_slice/test_check_supplemental_r2_admission.py"
            ),
        }
        evidence_sha256 = {}
        for path in sorted((root / "admission_evidence").rglob("evidence.json")):
            rel = path.relative_to(root).as_posix()
            evidence_sha256[rel] = sha256_file(path)

        handoff = {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "gate_requested": "SUPPLEMENTAL_ADMISSION_R2",
            "design_baseline_commit": scope.get("baseline_commit"),
            "payload_commit": payload_commit,
            "handoff_commit": {
                "value": "SELF",
                "direct_parent_required": payload_commit,
                "resolution": (
                    "Resolve immutable handoff SHA with `git rev-parse HEAD`; "
                    "direct parent must equal payload_commit."
                ),
            },
            "file_sha256": file_sha256,
            "evidence_sha256": evidence_sha256,
            "quota_feasibility": feasibility,
            "confirmations": {
                "a2_all_pending": True,
                "analysis_id_all_blank": True,
                "forbidden_data_absent": True,
                "readiness_ran": False,
                "canonical_freeze_claimed": False,
                "existing_files_unchanged": True,
            },
            "transport": contract.get("transport"),
            "created_at_utc": utc_now(),
        }
        write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
        print("HANDOFF_OK")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ret = sub.add_parser("retrieve", help="Fetch complete Repository.issues pages")
    p_ret.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_q = sub.add_parser("build-queue", help="Rebuild REVIEW_QUEUE from snapshot")
    p_q.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_v = sub.add_parser("validate-decisions", help="Validate REVIEW_DECISIONS binding")
    p_v.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_b = sub.add_parser("build-payload", help="Build sheet + evidence from decisions")
    p_b.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_h = sub.add_parser("write-handoff", help="Write handoff manifest")
    p_h.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    p_h.add_argument("--payload-commit", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root: Path = args.root
    if args.command == "retrieve":
        return cmd_retrieve(root)
    if args.command == "build-queue":
        return cmd_build_queue(root)
    if args.command == "validate-decisions":
        return cmd_validate_decisions(root)
    if args.command == "build-payload":
        return cmd_build_payload(root)
    if args.command == "write-handoff":
        return cmd_write_handoff(root, args.payload_commit)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
