#!/usr/bin/env python3
"""Field-level binding checker for supplemental mining R2 admission artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
PROHIBITED_VOCAB_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b|"
    r"(^|[^A-Za-z0-9_])(CE|OS|HP|TF|SI|fiber|stratum)([^A-Za-z0-9_]|$))"
)

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

QUEUE_COPIED = [
    "snapshot_record_id",
    "snapshot_record_sha256",
    "repository",
    "repository_order",
    "issue_node_id",
    "issue_number",
    "issue_url",
    "state",
    "created_at",
    "matched_phrases",
    "source_page_sha256",
]

DECISION_COPIED = [
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

SHEET_BOUND = [
    "neutral_id",
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
]

EVIDENCE_BOUND = [
    "neutral_id",
    "snapshot_record_id",
    "snapshot_record_sha256",
    "repository",
    "issue_node_id",
    "issue_number",
    "issue_url",
    "buggy_sha",
    "fixed_sha",
    "public_issue_url",
    "public_fix_url",
    "mechanism",
    "exclusion_class",
    "crit_real_public_fix",
    "crit_dual_arm_repro",
    "crit_in_numerical_scope",
    "decision",
]


class AdmissionError(Exception):
    pass


def fail(message: str) -> NoReturn:
    raise AdmissionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_miner():
    path = Path(__file__).resolve().parent / "mine_supplemental_r2.py"
    spec = importlib.util.spec_from_file_location("mine_supplemental_r2_for_checker", path)
    if spec is None or spec.loader is None:
        fail(f"unable to load miner from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_sheet(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != SHEET_HEADER:
            fail(f"sheet header mismatch: {reader.fieldnames}")
        return list(reader)


def verify_frozen_inputs(root: Path, scope: dict[str, Any]) -> None:
    for name in ("SCOPE.json", "TRANSPORT_CONTRACT.json", "QUOTAS.json"):
        if not (root / name).is_file():
            fail(f"missing frozen file {name}")
    transport = load_json(root / "TRANSPORT_CONTRACT.json")
    quotas = load_json(root / "QUOTAS.json")
    if scope.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("SCOPE task mismatch")
    if transport.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("TRANSPORT_CONTRACT task mismatch")
    if quotas.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("QUOTAS task mismatch")
    doc = transport.get("query_document") or ""
    if hashlib.sha256(doc.encode("utf-8")).hexdigest() != transport.get(
        "query_document_sha256"
    ):
        fail("query_document_sha256 drift")
    if transport.get("transport") != "github_graphql_repository_issues":
        fail("forbidden transport in contract")
    # Quota immutability checks against expected frozen shape.
    starting = quotas.get("starting_state") or {}
    if starting.get("accepted_ready_defects") != 18:
        fail("changed starting accepted_ready_defects")
    if starting.get("qualifying_projects") != 2:
        fail("changed starting qualifying_projects")
    order = quotas.get("readiness_quota_order") or []
    expected_repos = [
        "pymc-devs/pymc",
        "cornellius-gp/gpytorch",
        "jonathf/chaospy",
        "SALib/SALib",
        "pytorch/pytorch",
        "jax-ml/jax",
    ]
    if [e.get("repo") for e in order] != expected_repos:
        fail("quota repository order/replacement drift")
    expected_targets = [3, 3, 3, 3, 0, 0]
    if [int(e.get("additional_ready_target")) for e in order] != expected_targets:
        fail("quota target values changed")
    if quotas.get("replacement_policy") != "forbidden":
        fail("replacement_policy must be forbidden")
    projection = quotas.get("projection_if_quotas_met") or {}
    if int(projection.get("qualifying_projects", -1)) != 6:
        fail("incorrect J projection")
    if int(projection.get("ready_defects_lower_bound", -1)) != 30:
        fail("incorrect n projection")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_match_text(text: str) -> str:
    """Checker-owned NFC/casefold normalization for phrase surfaces."""
    return unicodedata.normalize("NFC", text or "").casefold()


def parse_created_at(value: str) -> datetime:
    # Python 3.11+ accepts trailing Z; keep checker-local and ruff-clean.
    return datetime.fromisoformat(value)


def validate_raw_issue_node(node: Any, *, repository: str) -> dict[str, Any]:
    """Independently enforce Issue shape, CLOSED state, URL, and complete labels."""
    if not isinstance(node, dict):
        fail(f"{repository}: raw node is not an object")
    typename = node.get("__typename")
    if typename != "Issue":
        fail(f"{repository}: typename not Issue: got {typename!r}")
    state = node.get("state")
    if state != "CLOSED":
        fail(f"{repository}: state not CLOSED: got {state!r}")
    closed_at = node.get("closedAt")
    if closed_at in (None, ""):
        fail(f"{repository}: closedAt missing/empty for issue {node.get('number')}")
    number = node.get("number")
    if not isinstance(number, int):
        fail(f"{repository}: issue number missing or non-int")
    if "/" not in repository:
        fail(f"{repository}: bad repository identity")
    owner, name = repository.split("/", 1)
    expected_url = f"https://github.com/{owner}/{name}/issues/{number}"
    url = node.get("url") or ""
    if url != expected_url or "/pull/" in url:
        fail(
            f"{repository}: canonical URL mismatch: got {url!r} expected {expected_url!r}"
        )
    for required in (
        "id",
        "title",
        "bodyText",
        "createdAt",
        "updatedAt",
        "closedAt",
    ):
        if required not in node or node[required] is None:
            fail(f"{repository}#{number}: missing required field {required}")
    if "labels" not in node or not isinstance(node["labels"], dict):
        fail(f"{repository}#{number}: labels must be an object")
    labels = node["labels"]
    if "pageInfo" not in labels or not isinstance(labels["pageInfo"], dict):
        fail(f"{repository}#{number}: labels.pageInfo must be an object")
    page_info = labels["pageInfo"]
    if "hasNextPage" not in page_info or page_info["hasNextPage"] is not False:
        fail(
            f"{repository}#{number}: incomplete labels "
            f"(hasNextPage must be false, got {page_info.get('hasNextPage')!r})"
        )
    label_nodes = labels.get("nodes")
    if not isinstance(label_nodes, list):
        fail(f"{repository}#{number}: labels.nodes missing")
    for lab in label_nodes:
        if not isinstance(lab, dict) or "name" not in lab:
            fail(f"{repository}#{number}: incomplete label entry")
    return node


def match_surfaces(issue: dict[str, Any], phrase: str) -> list[str]:
    """Checker-owned phrase surface matching over title/body/labels."""
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
    match_surfaces_map: dict[str, list[str]],
    source_page_index: int,
    source_page_sha256: str,
    query_document_sha256: str,
    variables_sha256: str,
    node_index: int,
    record_index: int,
) -> dict[str, Any]:
    """Checker-owned snapshot record construction and hashing."""
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
            p: list(match_surfaces_map.get(p, [])) for p in matched_phrases
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
    issues_with_meta: list[dict[str, Any]],
    query_document_sha256: str,
) -> list[dict[str, Any]]:
    """Checker-owned cutoff, per-phrase top-20, dedupe, ordering, and IDs."""
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
        matched = [p for p in phrases if p in entry["matched_phrases"]]
        records.append(
            build_snapshot_record(
                repository=repository,
                repository_order=repository_order,
                issue=item["issue"],
                matched_phrases=matched,
                match_surfaces_map=entry["match_surfaces"],
                source_page_index=item["source_page_index"],
                source_page_sha256=item["source_page_sha256"],
                query_document_sha256=query_document_sha256,
                variables_sha256=item["variables_sha256"],
                node_index=item["node_index"],
                record_index=idx,
            )
        )
    return records


def reconstruct_snapshot_records_from_raw_pages(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    """Rebuild ordered snapshot records from hash-bound pages without producer builders."""
    manifest = snapshot.get("page_manifest") or []
    if not isinstance(manifest, list) or not manifest:
        fail("snapshot page_manifest missing for reconstruction")
    query_sha = snapshot.get("query_document_sha256")
    if not isinstance(query_sha, str) or not query_sha:
        fail("snapshot query_document_sha256 missing for reconstruction")

    by_repo: dict[str, list[dict[str, Any]]] = {}
    for man in manifest:
        repo = str(man.get("repository"))
        by_repo.setdefault(repo, []).append(man)

    reconstructed: list[dict[str, Any]] = []
    for repo_entry in scope["repositories"]:
        repo = str(repo_entry["repo"])
        mans = by_repo.get(repo, [])
        issues_with_meta: list[dict[str, Any]] = []
        for man in mans:
            rel = man.get("path")
            if not isinstance(rel, str):
                fail(f"{repo}: manifest path missing")
            page_path = root / rel
            if not page_path.is_file():
                fail(f"{repo}: missing raw page {rel}")
            actual_sha = sha256_file(page_path)
            if actual_sha != man.get("sha256"):
                fail(f"{repo}: raw page sha256 drift for {rel}")
            payload = load_json(page_path)
            issues = _raw_issues_connection(payload)
            nodes = issues.get("nodes")
            if not isinstance(nodes, list):
                fail(f"{repo}: raw page nodes missing in {rel}")
            if len(nodes) != int(man.get("node_count", -1)):
                fail(f"{repo}: raw node_count drift in {rel}")
            page_index = int(man["page_index"])
            variables_sha = man.get("variables_sha256")
            if not isinstance(variables_sha, str):
                fail(f"{repo}: variables_sha256 missing in manifest page {page_index}")
            for node_index, node in enumerate(nodes):
                issue = validate_raw_issue_node(node, repository=repo)
                issues_with_meta.append(
                    {
                        "issue": issue,
                        "source_page_index": page_index,
                        "source_page_sha256": man["sha256"],
                        "variables_sha256": variables_sha,
                        "node_index": node_index,
                    }
                )
        records = select_phrase_union(
            scope=scope,
            repository=repo,
            repository_order=int(repo_entry["order"]),
            issues_with_meta=issues_with_meta,
            query_document_sha256=query_sha,
        )
        reconstructed.extend(records)
    return reconstructed


def verify_snapshot_bound_to_raw_pages(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
) -> None:
    """Exact field/order/cardinality compare vs independent raw-page reconstruction."""
    expected = reconstruct_snapshot_records_from_raw_pages(
        root, scope=scope, snapshot=snapshot
    )
    got = snapshot.get("records")
    if not isinstance(got, list):
        fail("snapshot records missing")
    if len(got) != len(expected):
        fail(
            f"snapshot cardinality mismatch: reconstructed={len(expected)} "
            f"committed={len(got)}"
        )
    for idx, (exp, rec) in enumerate(zip(expected, got)):
        if not isinstance(rec, dict):
            fail(f"snapshot record[{idx}] is not an object")
        if exp == rec:
            continue
        exp_keys = sorted(exp)
        got_keys = sorted(rec)
        if exp_keys != got_keys:
            fail(
                f"snapshot record[{idx}] key mismatch: "
                f"expected_keys={exp_keys} got_keys={got_keys}"
            )
        for key in exp_keys:
            if exp.get(key) != rec.get(key):
                fail(
                    f"snapshot record[{idx}] field mismatch on {key}: "
                    f"reconstructed={exp.get(key)!r} committed={rec.get(key)!r}"
                )
        fail(f"snapshot record[{idx}] mismatch without field delta")


def verify_snapshot_records(scope: dict[str, Any], snapshot: dict[str, Any]) -> None:
    records = snapshot.get("records") or []
    if not isinstance(records, list):
        fail("snapshot records missing")
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    phrases = list(scope["phrases"])
    for rec in records:
        required = [
            "snapshot_record_id",
            "repository",
            "repository_order",
            "issue_node_id",
            "issue_number",
            "issue_url",
            "state",
            "created_at",
            "updated_at",
            "closed_at",
            "title_sha256",
            "body_text_sha256",
            "ordered_labels",
            "matched_phrases",
            "match_surfaces",
            "source_page_index",
            "source_page_sha256",
            "query_document_sha256",
            "variables_sha256",
            "node_index",
            "snapshot_record_sha256",
        ]
        for field in required:
            if field not in rec:
                fail(f"snapshot missing field {field}")
        body = {k: rec[k] for k in required if k != "snapshot_record_sha256"}
        actual = canonical_sha256(body)
        if actual != rec["snapshot_record_sha256"]:
            fail(f"snapshot_record_sha256 mismatch for {rec['snapshot_record_id']}")
        if rec["state"] != "CLOSED":
            fail(f"snapshot state not CLOSED: {rec['snapshot_record_id']}")
        if "/pull/" in rec["issue_url"]:
            fail(f"pull URL in snapshot: {rec['issue_url']}")
        if rec["issue_url"] in seen_urls:
            fail(f"duplicate snapshot URL {rec['issue_url']}")
        if rec["issue_node_id"] in seen_ids:
            fail(f"duplicate snapshot node {rec['issue_node_id']}")
        seen_urls.add(rec["issue_url"])
        seen_ids.add(rec["issue_node_id"])
        matched = rec["matched_phrases"]
        if matched != [p for p in phrases if p in matched]:
            fail(f"phrase order wrong for {rec['snapshot_record_id']}")
        if not matched:
            fail(f"empty matched_phrases for {rec['snapshot_record_id']}")
        surfaces = rec["match_surfaces"]
        for phrase in matched:
            if phrase not in surfaces or not surfaces[phrase]:
                fail(f"match surface missing for {phrase}")
        repo_ok = any(r["repo"] == rec["repository"] for r in scope["repositories"])
        if not repo_ok:
            fail(f"repository outside scope: {rec['repository']}")


def verify_run_code_binding(root: Path, snapshot: dict[str, Any]) -> tuple[str, str]:
    """Field-by-field run_id/code_commit consistency across owner artifacts."""
    run_id = snapshot.get("run_id")
    code_commit = snapshot.get("code_commit")
    if not isinstance(run_id, str) or not run_id.strip():
        fail("snapshot missing run_id")
    if not isinstance(code_commit, str) or not FULL_SHA.fullmatch(code_commit):
        fail(f"snapshot illegal code_commit: {code_commit!r}")

    log_path = root / "COMMAND_LOG.json"
    if not log_path.is_file():
        fail("COMMAND_LOG.json missing")
    log = load_json(log_path)
    if log.get("run_id") != run_id:
        fail(
            f"command log run_id mismatch: log={log.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if log.get("code_commit") != code_commit:
        fail(
            f"command log code_commit mismatch: log={log.get('code_commit')!r} "
            f"snapshot={code_commit!r}"
        )
    entries = log.get("entries")
    if not isinstance(entries, list):
        fail("command log entries must be a list")
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"command log entry[{idx}] is not an object")
        if entry.get("run_id") != run_id:
            fail(
                f"command log entry[{idx}] run_id mismatch: "
                f"{entry.get('run_id')!r} != {run_id!r}"
            )
        if entry.get("code_commit") != code_commit:
            fail(
                f"command log entry[{idx}] code_commit mismatch: "
                f"{entry.get('code_commit')!r} != {code_commit!r}"
            )

    queue_path = root / "REVIEW_QUEUE.json"
    if not queue_path.is_file():
        fail("REVIEW_QUEUE.json missing")
    queue = load_json(queue_path)
    if queue.get("run_id") != run_id:
        fail(
            f"queue run_id mismatch: queue={queue.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if queue.get("code_commit") != code_commit:
        fail(
            f"queue code_commit mismatch: queue={queue.get('code_commit')!r} "
            f"snapshot={code_commit!r}"
        )

    publish_path = root / "PUBLISH_COMMIT.json"
    if not publish_path.is_file():
        fail("PUBLISH_COMMIT.json missing; sequential artifacts are incomplete")
    publish = load_json(publish_path)
    if publish.get("run_id") != run_id:
        fail(
            f"publish commit run_id mismatch: publish={publish.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if publish.get("code_commit") != code_commit:
        fail(
            f"publish commit code_commit mismatch: "
            f"publish={publish.get('code_commit')!r} snapshot={code_commit!r}"
        )

    diag_path = root / "RETRIEVAL_HARD_FAIL.json"
    if diag_path.is_file():
        diag = load_json(diag_path)
        if diag.get("run_id") != run_id:
            fail(
                f"diagnostic run_id mismatch: diag={diag.get('run_id')!r} "
                f"snapshot={run_id!r}"
            )
        if diag.get("code_commit") != code_commit:
            fail(
                f"diagnostic code_commit mismatch: "
                f"diag={diag.get('code_commit')!r} snapshot={code_commit!r}"
            )
        fail("success admission root must not contain RETRIEVAL_HARD_FAIL.json")

    return run_id, code_commit


def verify_publish_commit(
    root: Path,
    *,
    snapshot: dict[str, Any],
    miner: Any,
) -> dict[str, Any]:
    """Reject sequential partial publishes lacking a matching hash-bound identity."""
    publish_path = root / "PUBLISH_COMMIT.json"
    if not publish_path.is_file():
        fail("PUBLISH_COMMIT.json missing")
    publish = load_json(publish_path)
    page_files = {
        path.relative_to(root).as_posix(): miner.sha256_file(path)
        for path in sorted((root / "transport_pages").glob("*.json"))
    }
    expected = miner.build_publish_commit_identity(
        run_id=snapshot["run_id"],
        code_commit=snapshot["code_commit"],
        snapshot=snapshot,
        transport_page_sha256=page_files,
    )
    for field in (
        "run_id",
        "code_commit",
        "snapshot_sha256",
        "page_manifest_sha256",
        "transport_pages",
        "publish_commit_sha256",
    ):
        if publish.get(field) != expected.get(field):
            fail(f"publish commit field mismatch: {field}")
    return publish


def _raw_issues_connection(page_payload: dict[str, Any]) -> dict[str, Any]:
    data = page_payload.get("data")
    if not isinstance(data, dict):
        fail("transport page missing data")
    repo_obj = data.get("repository")
    if not isinstance(repo_obj, dict):
        fail("transport page missing repository")
    issues = repo_obj.get("issues")
    if not isinstance(issues, dict):
        fail("transport page missing issues connection")
    return issues


def verify_page_log_reconstruction(
    root: Path,
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Reconstruct page logs against manifest, hashes, variables, and continuity."""
    log = load_json(root / "COMMAND_LOG.json")
    entries = log.get("entries") or []
    page_entries = [e for e in entries if isinstance(e.get("page_index"), int)]
    if not page_entries:
        fail("command log has no page records")
    if any(not e.get("page_ok", False) for e in page_entries):
        fail("success admission root contains failed page log records")

    manifest = snapshot.get("page_manifest") or []
    if not isinstance(manifest, list) or not manifest:
        fail("snapshot page_manifest missing")
    if canonical_sha256(manifest) != snapshot.get("page_manifest_sha256"):
        fail("page_manifest_sha256 mismatch")
    if len(page_entries) != len(manifest):
        fail(
            f"page log/manifest cardinality mismatch: "
            f"log={len(page_entries)} manifest={len(manifest)}"
        )

    query_sha = contract.get("query_document_sha256")
    prev_by_repo: dict[str, dict[str, Any]] = {}
    for idx, (entry, man) in enumerate(zip(page_entries, manifest)):
        for field in (
            "repository",
            "page_index",
            "after",
            "endCursor",
            "hasNextPage",
            "variables_sha256",
            "response_page_sha256",
        ):
            if entry.get(field) != man.get(field):
                fail(f"page[{idx}] log/manifest mismatch on {field}")
        if entry.get("query_document_sha256") != query_sha:
            fail(f"page[{idx}] query_document_sha256 drift")
        if entry.get("operation_name") != contract.get("operation_name"):
            fail(f"page[{idx}] operation_name drift")
        variables = entry.get("variables")
        if not isinstance(variables, dict):
            fail(f"page[{idx}] variables missing")
        if man.get("variables") != variables:
            fail(f"page[{idx}] manifest variables mismatch")
        if canonical_sha256(variables) != entry.get("variables_sha256"):
            fail(f"page[{idx}] variables_sha256 reconstruction failed")
        if variables.get("after") != entry.get("after"):
            fail(f"page[{idx}] variables.after != after")
        rel = man.get("path")
        if not isinstance(rel, str) or not rel.startswith("transport_pages/"):
            fail(f"page[{idx}] invalid manifest path")
        page_path = root / rel
        if not page_path.is_file():
            fail(f"page[{idx}] missing transport page {rel}")
        actual_page_sha = sha256_file(page_path)
        if actual_page_sha != man.get("sha256"):
            fail(f"page[{idx}] transport page sha256 mismatch")
        if entry.get("exit_code") != 0:
            fail(f"page[{idx}] exit_code is nonzero in success log")
        if "endCursor" not in entry:
            fail(f"page[{idx}] missing verified endCursor")
        if "hasNextPage" not in entry:
            fail(f"page[{idx}] missing verified hasNextPage")

        repo = entry["repository"]
        prev = prev_by_repo.get(repo)
        if prev is None:
            if entry.get("after") is not None:
                fail(f"page[{idx}] first page after must be null")
            if entry.get("page_index") != 0:
                fail(f"page[{idx}] first page_index must be 0")
        else:
            if entry.get("after") != prev.get("endCursor"):
                fail(
                    f"page[{idx}] continuity break: after={entry.get('after')!r} "
                    f"prev.endCursor={prev.get('endCursor')!r}"
                )
            if entry.get("page_index") != int(prev.get("page_index")) + 1:
                fail(f"page[{idx}] page_index discontinuity")
        prev_by_repo[repo] = entry
    return page_entries


def verify_scope_page_coverage(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
    page_entries: list[dict[str, Any]],
) -> None:
    """Independently verify six-repo page blocks from SCOPE.json."""
    repos = scope.get("repositories") or []
    if not isinstance(repos, list) or len(repos) != 6:
        fail("SCOPE must list exactly six repositories")
    ordered = sorted(repos, key=lambda r: int(r.get("order", -1)))
    expected_repos = [str(r["repo"]) for r in ordered]
    if [int(r["order"]) for r in ordered] != [1, 2, 3, 4, 5, 6]:
        fail("SCOPE repository order must be fixed 1..6")
    if expected_repos != [str(r["repo"]) for r in repos]:
        fail("SCOPE repositories must already be listed in fixed order")

    manifest = snapshot.get("page_manifest") or []
    blocks: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    for man, entry in zip(manifest, page_entries):
        repo = str(man.get("repository"))
        if not blocks or blocks[-1][0] != repo:
            blocks.append((repo, [man], [entry]))
        else:
            blocks[-1][1].append(man)
            blocks[-1][2].append(entry)

    if [repo for repo, _, _ in blocks] != expected_repos:
        fail(
            "page blocks must cover SCOPE repositories in fixed order: "
            f"expected={expected_repos} got={[repo for repo, _, _ in blocks]}"
        )
    if any(repo != expected for (repo, _, _), expected in zip(blocks, expected_repos)):
        fail("page block repository identity drift vs SCOPE")

    # Shared across all six repositories; issue numbers remain per-repo.
    global_node_ids: set[str] = set()
    global_urls: set[str] = set()

    for repo, mans, logs in blocks:
        if not mans:
            fail(f"empty page block for {repo}")
        if "/" not in repo:
            fail(f"SCOPE repository not owner/name: {repo}")
        scope_owner, scope_name = repo.split("/", 1)
        for i, (man, entry) in enumerate(zip(mans, logs)):
            if int(man.get("page_index", -1)) != i or int(entry.get("page_index", -1)) != i:
                fail(f"{repo}: page block must be contiguous starting at 0")
            if man.get("repository_order") != ordered[expected_repos.index(repo)]["order"]:
                fail(f"{repo}: repository_order mismatch vs SCOPE")

            page_payload = load_json(root / man["path"])
            issues = _raw_issues_connection(page_payload)
            page_info = issues.get("pageInfo") or {}
            raw_has_next = page_info.get("hasNextPage")
            raw_end = page_info.get("endCursor")
            if raw_has_next is not True and raw_has_next is not False:
                fail(f"{repo} page {i}: raw hasNextPage must be boolean")
            if man.get("hasNextPage") != raw_has_next:
                fail(f"{repo} page {i}: manifest hasNextPage != raw pageInfo")
            if entry.get("hasNextPage") != raw_has_next:
                fail(f"{repo} page {i}: log hasNextPage != raw pageInfo")
            if man.get("endCursor") != raw_end:
                fail(f"{repo} page {i}: manifest endCursor != raw pageInfo")
            if entry.get("endCursor") != raw_end:
                fail(f"{repo} page {i}: log endCursor != raw pageInfo")

            is_last = i == len(mans) - 1
            if is_last:
                if raw_has_next is not False:
                    fail(f"{repo}: last page must terminate (hasNextPage=false)")
            else:
                if raw_has_next is not True:
                    fail(f"{repo}: middle page {i} must continue (hasNextPage=true)")
                if not raw_end:
                    fail(f"{repo}: middle page {i} missing endCursor")

        first_total: int | None = None
        seen_numbers: set[int] = set()
        node_total = 0
        for i, man in enumerate(mans):
            issues = _raw_issues_connection(load_json(root / man["path"]))
            total_count = issues.get("totalCount")
            if not isinstance(total_count, int):
                fail(f"{repo} page {i}: totalCount missing")
            if first_total is None:
                first_total = total_count
            elif total_count != first_total:
                fail(
                    f"{repo}: totalCount drift page {i}: "
                    f"{total_count} != {first_total}"
                )
            if man.get("totalCount") != total_count:
                fail(f"{repo} page {i}: manifest totalCount != raw")
            nodes = issues.get("nodes")
            if not isinstance(nodes, list):
                fail(f"{repo} page {i}: nodes missing")
            if man.get("node_count") != len(nodes):
                fail(f"{repo} page {i}: manifest node_count != raw nodes")
            node_total += len(nodes)
            for node in nodes:
                if not isinstance(node, dict):
                    fail(f"{repo} page {i}: node is not an object")
                node_id = node.get("id")
                number = node.get("number")
                url = node.get("url")
                if not isinstance(node_id, str) or not node_id:
                    fail(f"{repo} page {i}: node id missing")
                if not isinstance(number, int):
                    fail(f"{repo} page {i}: node number missing")
                if not isinstance(url, str) or not url:
                    fail(f"{repo} page {i}: node url missing")
                # Shared six-repo uniqueness before per-repo URL binding.
                if node_id in global_node_ids:
                    fail(
                        f"duplicate node id across SCOPE repositories: {node_id}"
                    )
                if url in global_urls:
                    fail(
                        f"duplicate node url across SCOPE repositories: {url}"
                    )
                if number in seen_numbers:
                    fail(f"{repo}: duplicate node number {number}")
                expected_url = (
                    f"https://github.com/{scope_owner}/{scope_name}/issues/{number}"
                )
                if url != expected_url:
                    fail(
                        f"{repo} page {i}: URL owner/repository mismatch: "
                        f"got {url!r} expected {expected_url!r}"
                    )
                global_node_ids.add(node_id)
                global_urls.add(url)
                seen_numbers.add(number)
        assert first_total is not None
        if node_total != first_total:
            fail(
                f"{repo}: node total {node_total} != totalCount {first_total}"
            )


def verify_queue_binding(
    miner: Any, scope: dict[str, Any], snapshot: dict[str, Any], queue: dict[str, Any]
) -> list[dict[str, Any]]:
    if queue.get("run_id") != snapshot.get("run_id"):
        fail(
            f"queue/snapshot run_id mismatch: queue={queue.get('run_id')!r} "
            f"snapshot={snapshot.get('run_id')!r}"
        )
    if queue.get("code_commit") != snapshot.get("code_commit"):
        fail(
            f"queue/snapshot code_commit mismatch: "
            f"queue={queue.get('code_commit')!r} "
            f"snapshot={snapshot.get('code_commit')!r}"
        )
    expected = miner.build_queue_from_snapshot(scope, snapshot)
    got = queue.get("records") or []
    if len(got) != len(expected):
        fail(f"queue cardinality mismatch expected={len(expected)} got={len(got)}")
    # Compare semantic records ignoring review_status mutations after payload build.
    def semantic(row: dict[str, Any]) -> dict[str, Any]:
        out = dict(row)
        # review_status may be updated by build-payload; compare core identity fields.
        return {k: out.get(k) for k in (
            "neutral_id",
            "union_order",
            "repository_review_order",
            *QUEUE_COPIED,
        )}

    for idx, (exp, row) in enumerate(zip(expected, got)):
        if semantic(exp) != semantic(row):
            fail(f"queue row mismatch at index {idx}: {row.get('neutral_id')}")
        if row.get("union_order") != idx % 10**9 and row.get("repository_review_order") != row.get(
            "union_order"
        ):
            # Contiguity per repository checked below.
            pass
        snap = next(
            r
            for r in snapshot["records"]
            if r["snapshot_record_id"] == row["snapshot_record_id"]
        )
        for field in QUEUE_COPIED:
            if row.get(field) != snap.get(field):
                fail(f"queue/snapshot field mismatch {row['neutral_id']}:{field}")
        if row.get("snapshot_record_sha256") != snap.get("snapshot_record_sha256"):
            fail(f"queue snapshot hash mismatch {row['neutral_id']}")

    # Contiguous IDs / orders per repository.
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in got:
        by_repo.setdefault(row["repository"], []).append(row)
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        rows = by_repo.get(repo, [])
        for i, row in enumerate(rows, start=1):
            if row["union_order"] != i or row["repository_review_order"] != i:
                fail(f"noncontiguous order in {repo}: {row['neutral_id']}")
            expected_id = f"{repo_entry['id_prefix']}{i:02d}"
            if row["neutral_id"] != expected_id:
                fail(f"wrong neutral_id: got {row['neutral_id']} expected {expected_id}")
    return got


def review_stop_reason(
    *,
    decision_count: int,
    queue_count: int,
    pending_count: int,
    max_reviewed: int,
    target_pending: int,
) -> str:
    """Independent stop-reason classifier (mirrors producer; no producer import)."""
    if decision_count == queue_count:
        return "queue_exhausted"
    if pending_count >= target_pending:
        return "five_admit_pending_repro"
    if decision_count >= max_reviewed:
        return "twenty_reviewed"
    return "invalid_early_stop"


def verify_decisions(
    scope: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    decisions = decisions_payload.get("decisions") or []
    exclusion_classes = set(scope["exclusion_classes"])
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])

    by_repo_q: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo_q.setdefault(row["repository"], []).append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {}
    for d in decisions:
        by_repo_d.setdefault(d["repository"], []).append(d)

    for repo, qrows in by_repo_q.items():
        dreviews = by_repo_d.get(repo, [])
        if not dreviews and qrows:
            fail(f"no decisions for non-empty queue: {repo}")
        for idx, decision in enumerate(dreviews):
            if idx >= len(qrows):
                fail(f"extra decision for {repo}")
            qrow = qrows[idx]
            if qrow.get("review_status") == "NOT_REVIEWED_AFTER_STOP":
                fail(f"decision for NOT_REVIEWED_AFTER_STOP: {decision.get('neutral_id')}")
            for field in DECISION_COPIED:
                if decision.get(field) != qrow.get(field):
                    fail(
                        f"decision/queue mismatch {decision.get('neutral_id')}:{field}"
                    )
            if decision.get("crit_dual_arm_repro") != "PENDING":
                fail(f"non-PENDING A2 for {decision.get('neutral_id')}")
            if decision.get("analysis_id") not in (None, ""):
                fail(f"nonblank analysis_id for {decision.get('neutral_id')}")
            a1 = decision.get("crit_real_public_fix")
            a3 = decision.get("crit_in_numerical_scope")
            verdict = decision.get("decision")
            excl = decision.get("exclusion_class") or ""
            for text_key in ("mechanism", "decision_reason"):
                if PROHIBITED_VOCAB_RE.search(decision.get(text_key) or ""):
                    fail(f"forbidden vocabulary in {decision.get('neutral_id')}:{text_key}")
            if a1 == "PASS":
                for field in ("buggy_sha", "fixed_sha"):
                    if not FULL_SHA.match(str(decision.get(field) or "")):
                        fail(f"short SHA {decision.get('neutral_id')}:{field}")
                for field in ("public_issue_url", "public_fix_url"):
                    if not decision.get(field):
                        fail(f"missing public URL {decision.get('neutral_id')}:{field}")
            if verdict == "ADMIT_PENDING_REPRO":
                if a1 != "PASS" or a3 != "PASS" or excl:
                    fail(f"ADMIT inconsistency {decision.get('neutral_id')}")
            elif verdict == "EXCLUDED":
                if excl and excl not in exclusion_classes:
                    fail(f"invalid exclusion class {excl}")
                if not excl and a1 == "PASS" and a3 == "PASS":
                    fail(f"excluded without class/failure {decision.get('neutral_id')}")
            else:
                fail(f"invalid decision {verdict}")

        pending = sum(1 for d in dreviews if d.get("decision") == "ADMIT_PENDING_REPRO")
        decision_count = len(dreviews)
        queue_count = len(qrows)
        if decision_count > max_reviewed:
            fail(f"reviewed over cap for {repo}")
        if pending > target_pending:
            fail(f"pending over cap for {repo}")
        if decision_count > queue_count:
            fail(f"extra decision for {repo}")
        if decision_count < queue_count:
            if not (
                pending >= target_pending or decision_count >= max_reviewed
            ):
                fail(
                    f"invalid early stop for {repo}: "
                    f"decisions={decision_count}, queue={queue_count}, pending={pending}"
                )
        reason = review_stop_reason(
            decision_count=decision_count,
            queue_count=queue_count,
            pending_count=pending,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        if reason == "invalid_early_stop":
            fail(f"invalid early stop for {repo}")

        # Queue review_status may be PENDING_REVIEW before build-payload restamps,
        # but must never claim REVIEWED beyond the decided prefix, nor leave a
        # decided row marked NOT_REVIEWED_AFTER_STOP.
        for idx, qrow in enumerate(qrows):
            status = qrow.get("review_status")
            if idx < decision_count:
                if status == "NOT_REVIEWED_AFTER_STOP":
                    fail(
                        f"decision for NOT_REVIEWED_AFTER_STOP: "
                        f"{qrow.get('neutral_id')}"
                    )
            elif status == "REVIEWED":
                fail(
                    f"omitted reviewed decision for {qrow.get('neutral_id')}: "
                    "queue row marked REVIEWED without a decision"
                )

    # Global decision order must equal concatenation of per-repo reviewed prefixes
    # in repository order.
    expected_ids: list[str] = []
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        expected_ids.extend(d["neutral_id"] for d in by_repo_d.get(repo, []))
    got_ids = [d["neutral_id"] for d in decisions]
    if got_ids != expected_ids:
        # Allow decisions list already in repo order; otherwise fail reorder.
        if sorted(got_ids) == sorted(expected_ids) and got_ids != expected_ids:
            fail("reordered decisions")
    return decisions


def verify_sheet_and_evidence(
    decisions: list[dict[str, Any]],
    sheet_rows: list[dict[str, str]],
    evidence_snapshot: dict[str, Any],
    root: Path,
) -> None:
    if len(sheet_rows) != len(decisions):
        fail(
            f"sheet/decision cardinality mismatch "
            f"{len(sheet_rows)} != {len(decisions)}"
        )
    manifest = evidence_snapshot.get("records") or []
    if len(manifest) != len(decisions):
        fail("evidence manifest cardinality mismatch")
    seen_evidence: set[str] = set()
    for decision, row, man in zip(decisions, sheet_rows, manifest):
        nid = decision["neutral_id"]
        if row.get("neutral_id") != nid or man.get("neutral_id") != nid:
            fail(f"sheet/evidence order mismatch around {nid}")
        if row.get("source_cohort") != "supplemental_r2":
            fail(f"wrong cohort for {nid}")
        if row.get("analysis_id") not in (None, ""):
            fail(f"nonblank alias for {nid}")
        if row.get("crit_dual_arm_repro") != "PENDING":
            fail(f"sheet A2 not PENDING for {nid}")
        for field in SHEET_BOUND:
            sheet_val = row.get(field) or ""
            if field == "mechanism":
                dec_val = decision.get("mechanism") or ""
            elif field == "decision_reason":
                dec_val = decision.get("decision_reason") or ""
            elif field in {
                "buggy_sha",
                "fixed_sha",
                "crit_real_public_fix",
                "crit_dual_arm_repro",
                "crit_in_numerical_scope",
                "decision",
                "neutral_id",
                "repository",
                "issue_url",
            }:
                dec_val = str(decision.get(field) or "")
                if field == "crit_dual_arm_repro":
                    dec_val = "PENDING"
            else:
                dec_val = str(decision.get(field) or "")
            if sheet_val != dec_val:
                fail(f"sheet/decision mismatch {nid}:{field}")
        for text_key in ("mechanism", "decision_reason"):
            if PROHIBITED_VOCAB_RE.search(row.get(text_key) or ""):
                fail(f"forbidden vocabulary in sheet {nid}:{text_key}")

        rel = (man.get("path") or "").replace("\\", "/")
        candidates = [
            root / "admission_evidence" / nid / "evidence.json",
            root / rel,
            Path.cwd() / rel,
        ]
        if "admission_evidence/" in rel:
            suffix = rel.split("admission_evidence/", 1)[1]
            candidates.insert(0, root / "admission_evidence" / suffix)
        candidate = next((p for p in candidates if p.is_file()), None)
        if candidate is None:
            fail(f"missing evidence file for {nid}: {rel}")
        actual_sha = sha256_file(candidate)
        if actual_sha != man.get("sha256"):
            fail(f"evidence hash mismatch for {nid}")
        if nid in seen_evidence:
            fail(f"duplicate evidence for {nid}")
        seen_evidence.add(nid)
        evidence = load_json(candidate)
        for field in EVIDENCE_BOUND:
            if field == "crit_dual_arm_repro":
                if evidence.get(field) != "PENDING":
                    fail(f"evidence A2 not PENDING for {nid}")
                continue
            if evidence.get(field) != decision.get(field) and not (
                (evidence.get(field) in (None, ""))
                and (decision.get(field) in (None, ""))
            ):
                # string normalize
                if str(evidence.get(field) or "") != str(decision.get(field) or ""):
                    fail(f"evidence/decision mismatch {nid}:{field}")
        if evidence.get("analysis_id") not in (None, ""):
            fail(f"evidence nonblank analysis_id for {nid}")
        # Cross-check sheet vs evidence for overlapping fields.
        for field in (
            "neutral_id",
            "repository",
            "issue_url",
            "buggy_sha",
            "fixed_sha",
            "mechanism",
            "crit_real_public_fix",
            "crit_dual_arm_repro",
            "crit_in_numerical_scope",
            "decision",
        ):
            if str(row.get(field) or "") != str(evidence.get(field) or ""):
                fail(f"sheet/evidence mismatch {nid}:{field}")


def verify_quota_disclosure(
    quotas: dict[str, Any], decisions: list[dict[str, Any]], handoff: dict[str, Any] | None
) -> None:
    miner = _load_miner()
    feasibility = miner.project_quota_feasibility(quotas, decisions)
    if handoff is None:
        return
    claimed = handoff.get("quota_feasibility") or {}
    if claimed.get("claims_ready_success"):
        fail("handoff claims ready success")
    if claimed.get("claims_readiness_executed"):
        fail("handoff claims readiness execution")
    if claimed.get("claims_canonical_freeze"):
        fail("handoff claims canonical freeze")
    if feasibility["status"] == quotas["shortfall_status"]:
        if not claimed.get("shortfalls"):
            fail("missing shortfall disclosure")
    if claimed.get("starting_accepted_ready_defects") != 18:
        fail("handoff starting count drift")
    proj = claimed.get("projection_if_quotas_met") or {}
    if int(proj.get("qualifying_projects", -1)) != 6:
        fail("handoff incorrect J projection")
    if int(proj.get("ready_defects_lower_bound", -1)) != 30:
        fail("handoff incorrect n projection")


def verify_admission(root: Path) -> int:
    """Library entry point: return 0 on success, nonzero on failure."""
    try:
        if not root.is_dir():
            fail(f"root not a directory: {root}")
        scope = load_json(root / "SCOPE.json")
        verify_frozen_inputs(root, scope)
        miner = _load_miner()
        snapshot = load_json(root / "ISSUE_SNAPSHOT.json")
        verify_run_code_binding(root, snapshot)
        contract = load_json(root / "TRANSPORT_CONTRACT.json")
        page_entries = verify_page_log_reconstruction(
            root, snapshot=snapshot, contract=contract
        )
        verify_scope_page_coverage(
            root,
            scope=scope,
            snapshot=snapshot,
            page_entries=page_entries,
        )
        verify_snapshot_bound_to_raw_pages(root, scope=scope, snapshot=snapshot)
        verify_snapshot_records(scope, snapshot)
        queue_payload = load_json(root / "REVIEW_QUEUE.json")
        verify_publish_commit(root, snapshot=snapshot, miner=miner)
        queue = verify_queue_binding(miner, scope, snapshot, queue_payload)
        decisions_payload = load_json(root / "REVIEW_DECISIONS.json")
        decisions = verify_decisions(scope, queue, decisions_payload)
        sheet_path = root / "admission_sheet.cursor_candidate.csv"
        sheet_rows = read_sheet(sheet_path)
        evidence_snapshot = load_json(root / "EVIDENCE_SNAPSHOT.json")
        verify_sheet_and_evidence(decisions, sheet_rows, evidence_snapshot, root)
        quotas = load_json(root / "QUOTAS.json")
        handoff_path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
        handoff = load_json(handoff_path) if handoff_path.is_file() else None
        verify_quota_disclosure(quotas, decisions, handoff)
        # Blind / forbidden confirmations when handoff present.
        if handoff is not None:
            conf = handoff.get("confirmations") or {}
            if conf.get("readiness_ran"):
                fail("handoff reports readiness ran")
            if conf.get("canonical_freeze_claimed"):
                fail("handoff reports canonical freeze")
            if not conf.get("a2_all_pending", False):
                fail("handoff missing a2_all_pending confirmation")
        print("ADMISSION_CHECK_OK")
        return 0
    except AdmissionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: unexpected: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/external_slice/supplemental_r2"),
    )
    args = parser.parse_args(argv)
    return verify_admission(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
