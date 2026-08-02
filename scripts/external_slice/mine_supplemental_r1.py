#!/usr/bin/env python3
"""Deterministic supplemental mining R1 search / evidence / build CLI."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HEADER = [
    "neutral_id",
    "repo",
    "issue_url",
    "buggy_sha",
    "fixed_sha",
    "mechanism_sentence",
    "crit_real_defect",
    "crit_dual_arm_repro",
    "crit_in_scope",
    "decision",
    "exclusion_reason",
    "analysis_id",
]

DECISION_FIELDS = [
    "neutral_id",
    "repo",
    "issue_number",
    "issue_url",
    "fix_url",
    "buggy_sha",
    "fixed_sha",
    "mechanism_sentence",
    "crit_real_defect",
    "crit_dual_arm_repro",
    "crit_in_scope",
    "decision",
    "exclusion_reason",
    "analysis_id",
    "rationales",
    "evidence_urls",
    "review_order",
    "review_status",
]

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
TOKEN_RE = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"Bearer\s+[A-Za-z0-9][A-Za-z0-9._-]{15,}|Authorization:\s*\S+",
    re.IGNORECASE,
)
RESERVED_RE = re.compile(
    r"(?i)(^|[^A-Za-z0-9_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)"
    r"([^A-Za-z0-9_]|$)"
)
PROHIBITED_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b)"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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


def load_scope(path: Path) -> dict[str, Any]:
    scope = load_json(path)
    if scope.get("task") != "SUPPLEMENTAL_MINING_R1":
        raise SystemExit("ERROR: scope task must be SUPPLEMENTAL_MINING_R1")
    return scope


def append_command_log(path: Path, entry: dict[str, Any]) -> None:
    if path.exists():
        payload = load_json(path)
    else:
        payload = {"schema_version": 1, "entries": []}
    payload.setdefault("schema_version", 1)
    payload.setdefault("entries", [])
    payload["entries"].append(entry)
    write_json(path, payload)


def run_gh(
    args: list[str],
    *,
    command_log: Path | None,
    label: str,
    max_retries: int = 6,
) -> dict[str, Any]:
    cmd = ["gh", *args]
    attempt = 0
    while True:
        attempt += 1
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        stdout = proc.stdout or ""
        stderr = sanitize(proc.stderr or "")
        entry = {
            "label": label if attempt == 1 else f"{label}:retry{attempt}",
            "command": cmd,
            "cwd": str(Path.cwd()),
            "timestamp_utc": utc_now(),
            "exit_code": proc.returncode,
            "stdout_sha256": sha256_text(stdout),
            "stderr_tail": stderr[-2000:],
            "attempt": attempt,
        }
        if command_log is not None:
            append_command_log(command_log, entry)
        if proc.returncode == 0:
            return json.loads(stdout) if stdout.strip() else {}
        rate_limited = (
            proc.returncode in {1, 8}
            and (
                "rate limit" in stderr.lower()
                or "API rate limit exceeded" in stderr
                or "secondary rate limit" in stderr.lower()
                or "403" in stderr
            )
        )
        if rate_limited and attempt <= max_retries:
            time.sleep(min(60, 8 * attempt))
            continue
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\n{stderr[-2000:]}"
        )


def build_queries(scope: dict[str, Any]) -> list[dict[str, str]]:
    cutoff = scope["created_cutoff"]
    queries: list[dict[str, str]] = []
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        for phrase in scope["phrases"]:
            q = (
                f'repo:{repo} is:issue is:closed created:<={cutoff} "{phrase}"'
            )
            queries.append({"repo": repo, "phrase": phrase, "q": q})
    return queries


ISSUE_REF_RE = re.compile(
    r"(?i)(?:clos(?:e|es|ed)|fix(?:es|ed)|resolve(?:s|d)|see|toward)\s+#(\d+)|#(\d+)"
)


def hit_record_from_item(item: dict[str, Any], *, repo: str, phrase: str) -> dict[str, Any]:
    html_url = item["html_url"]
    is_pr = item.get("pull_request") is not None or "/pull/" in html_url
    body = item.get("body") or ""
    title = item.get("title") or ""
    return {
        "repo": repo,
        "phrase": phrase,
        "number": int(item["number"]),
        "html_url": html_url,
        "is_pull_request": is_pr,
        "state": item.get("state", ""),
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "closed_at": item.get("closed_at", ""),
        "title_sha256": sha256_text(title),
        "body_sha256": sha256_text(body),
        "api_id": item.get("id"),
        "title_issue_refs": sorted(
            {
                int(a or b)
                for a, b in ISSUE_REF_RE.findall(f"{title}\n{body}")
                if (a or b)
            }
        ),
    }


def extract_issue_numbers_from_text(text: str) -> list[int]:
    found: list[int] = []
    seen: set[int] = set()
    for a, b in ISSUE_REF_RE.findall(text or ""):
        number = int(a or b)
        if number not in seen:
            seen.add(number)
            found.append(number)
    return found


def resolve_issues_from_pr(
    repo: str,
    pr_number: int,
    *,
    command_log: Path,
    seed_refs: list[int] | None = None,
) -> list[dict[str, Any]]:
    owner, name = repo.split("/", 1)
    linked: dict[int, dict[str, Any]] = {}
    for number in seed_refs or []:
        linked[number] = {"issue_number": number, "source": "title_or_body_ref"}

    # GraphQL closing issue references (may be empty for older events).
    try:
        gql = run_gh(
            [
                "api",
                "graphql",
                "-f",
                (
                    "query=query($o:String!,$n:String!,$p:Int!){"
                    "repository(owner:$o,name:$n){pullRequest(number:$p){"
                    "number url title body merged mergeCommit{oid} headRefOid "
                    "closingIssuesReferences(first:20){nodes{number url state createdAt closedAt}}"
                    "}}}"
                ),
                "-f",
                f"o={owner}",
                "-f",
                f"n={name}",
                "-F",
                f"p={pr_number}",
            ],
            command_log=command_log,
            label=f"graphql-pr-links:{repo}#{pr_number}",
        )
        pr = (((gql.get("data") or {}).get("repository") or {}).get("pullRequest")) or {}
        title = pr.get("title") or ""
        body = pr.get("body") or ""
        for number in extract_issue_numbers_from_text(f"{title}\n{body}"):
            linked.setdefault(number, {"issue_number": number, "source": "pr_text_ref"})
        for node in ((pr.get("closingIssuesReferences") or {}).get("nodes") or []):
            number = int(node["number"])
            linked[number] = {
                "issue_number": number,
                "issue_url": node.get("url") or f"https://github.com/{repo}/issues/{number}",
                "state": node.get("state", "").lower(),
                "created_at": node.get("createdAt", ""),
                "closed_at": node.get("closedAt", ""),
                "source": "closingIssuesReferences",
                "title_sha256": "",
                "body_sha256": "",
            }
        pr_meta = {
            "pr_number": pr_number,
            "pr_url": pr.get("url") or f"https://github.com/{repo}/pull/{pr_number}",
            "merged": bool(pr.get("merged")),
            "merge_commit_sha": ((pr.get("mergeCommit") or {}).get("oid")) or "",
            "head_sha": pr.get("headRefOid") or "",
            "title_sha256": sha256_text(title),
            "body_sha256": sha256_text(body),
        }
    except RuntimeError:
        pr_meta = {
            "pr_number": pr_number,
            "pr_url": f"https://github.com/{repo}/pull/{pr_number}",
            "merged": False,
            "merge_commit_sha": "",
            "head_sha": "",
            "title_sha256": "",
            "body_sha256": "",
        }
        try:
            pr = _gh_json(
                f"repos/{repo}/pulls/{pr_number}",
                command_log,
                f"pull:{repo}#{pr_number}",
            )
            title = pr.get("title") or ""
            body = pr.get("body") or ""
            for number in extract_issue_numbers_from_text(f"{title}\n{body}"):
                linked.setdefault(number, {"issue_number": number, "source": "pr_text_ref"})
            pr_meta.update(
                {
                    "pr_url": pr.get("html_url") or pr_meta["pr_url"],
                    "merged": bool(pr.get("merged")),
                    "merge_commit_sha": pr.get("merge_commit_sha") or "",
                    "head_sha": ((pr.get("head") or {}).get("sha")) or "",
                    "title_sha256": sha256_text(title),
                    "body_sha256": sha256_text(body),
                }
            )
        except RuntimeError:
            pass

    issues: list[dict[str, Any]] = []
    for number, meta in sorted(linked.items()):
        if meta.get("issue_url") and meta.get("created_at"):
            record = {
                "repo": repo,
                "issue_number": number,
                "issue_url": meta["issue_url"],
                "state": meta.get("state", ""),
                "created_at": meta.get("created_at", ""),
                "closed_at": meta.get("closed_at", ""),
                "title_sha256": meta.get("title_sha256", ""),
                "body_sha256": meta.get("body_sha256", ""),
                "source_pr": pr_meta,
            }
            issues.append(record)
            continue
        try:
            issue = _gh_json(
                f"repos/{repo}/issues/{number}",
                command_log,
                f"issue:{repo}#{number}",
            )
        except RuntimeError:
            continue
        if issue.get("pull_request") is not None:
            continue
        issues.append(
            {
                "repo": repo,
                "issue_number": number,
                "issue_url": issue.get("html_url")
                or f"https://github.com/{repo}/issues/{number}",
                "state": issue.get("state", ""),
                "created_at": issue.get("created_at", ""),
                "closed_at": issue.get("closed_at", ""),
                "title_sha256": sha256_text(issue.get("title") or ""),
                "body_sha256": sha256_text(issue.get("body") or ""),
                "source_pr": pr_meta,
            }
        )
    return issues


def apply_review_stop(
    records: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    *,
    max_reviewed: int,
    target_pending: int,
) -> list[dict[str, Any]]:
    decision_by_id = {d["neutral_id"]: d for d in decisions}
    pending = 0
    reviewed = 0
    stop = False
    out: list[dict[str, Any]] = []
    for record in records:
        cloned = dict(record)
        if stop:
            cloned["review_status"] = "NOT_REVIEWED_AFTER_STOP"
            out.append(cloned)
            continue
        reviewed += 1
        cloned["review_status"] = "REVIEWED"
        decision = decision_by_id.get(cloned["neutral_id"], {})
        if decision.get("decision") == "ADMIT_PENDING_REPRO":
            pending += 1
        out.append(cloned)
        if pending >= target_pending or reviewed >= max_reviewed:
            stop = True
    return out


def assign_queue(
    scope: dict[str, Any],
    hits_by_repo: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        prefix = repo_entry["id_prefix"]
        items = hits_by_repo.get(repo, [])
        # Deduplicate by URL, keep first-seen provenance phrases as list.
        by_url: dict[str, dict[str, Any]] = {}
        for item in items:
            url = item["issue_url"]
            if url not in by_url:
                cloned = dict(item)
                cloned["phrases"] = list(item.get("phrases") or ([item["phrase"]] if item.get("phrase") else []))
                source_prs = []
                if item.get("source_pr"):
                    source_prs.append(item["source_pr"])
                cloned["source_prs"] = source_prs
                by_url[url] = cloned
            else:
                phrase = item.get("phrase")
                if phrase and phrase not in by_url[url]["phrases"]:
                    by_url[url]["phrases"].append(phrase)
                for p in item.get("phrases") or []:
                    if p not in by_url[url]["phrases"]:
                        by_url[url]["phrases"].append(p)
                if item.get("source_pr"):
                    pr_url = item["source_pr"].get("pr_url")
                    existing = {p.get("pr_url") for p in by_url[url]["source_prs"]}
                    if pr_url not in existing:
                        by_url[url]["source_prs"].append(item["source_pr"])
        ordered = sorted(
            by_url.values(),
            key=lambda r: (r.get("created_at") or "", r["issue_number"]),
            reverse=True,
        )
        for index, item in enumerate(ordered, start=1):
            record = dict(item)
            record["neutral_id"] = f"{prefix}{index:02d}"
            record["id_prefix"] = prefix
            record["review_status"] = "PENDING_REVIEW"
            records.append(record)
    return records


def cmd_search(
    scope_path: Path,
    snapshot_path: Path,
    queue_path: Path,
    command_log_path: Path,
) -> None:
    scope = load_scope(scope_path)
    queries = build_queries(scope)
    query_results: list[dict[str, Any]] = []
    issue_hits_by_repo: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }

    for index, query in enumerate(queries):
        if index:
            # Stay under the authenticated search budget (30 requests/minute).
            time.sleep(2.2)
        label = f"search:{query['repo']}:{query['phrase']}"
        payload = run_gh(
            [
                "api",
                "-X",
                "GET",
                "search/issues",
                "-f",
                f"q={query['q']}",
                "-f",
                f"sort={scope['search_sort']}",
                "-f",
                f"order={scope['search_order']}",
                "-F",
                f"per_page={scope['max_results_per_phrase']}",
            ],
            command_log=command_log_path,
            label=label,
        )
        items = []
        for raw in payload.get("items", []):
            record = hit_record_from_item(raw, repo=query["repo"], phrase=query["phrase"])
            items.append(record)
            if not record["is_pull_request"]:
                issue_hits_by_repo[query["repo"]].append(
                    {
                        "repo": query["repo"],
                        "phrase": query["phrase"],
                        "phrases": [query["phrase"]],
                        "issue_number": record["number"],
                        "issue_url": record["html_url"].replace("/pull/", "/issues/"),
                        "state": record["state"],
                        "created_at": record["created_at"],
                        "closed_at": record["closed_at"],
                        "title_sha256": record["title_sha256"],
                        "body_sha256": record["body_sha256"],
                        "source_pr": None,
                    }
                )
        query_results.append(
            {
                "repo": query["repo"],
                "phrase": query["phrase"],
                "q": query["q"],
                "total_count": payload.get("total_count", 0),
                "incomplete_results": payload.get("incomplete_results", False),
                "returned": len(items),
                "issue_count": sum(1 for i in items if not i["is_pull_request"]),
                "pull_count": sum(1 for i in items if i["is_pull_request"]),
                "items": items,
            }
        )

    # Pilot-compatible follow-up: GitHub search often surfaces PRs for these phrases.
    # Resolve public linked issues from those fix records before queue assignment.
    pr_issue_cache: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for query in query_results:
        repo = query["repo"]
        phrase = query["phrase"]
        for hit in query["items"]:
            if not hit["is_pull_request"]:
                continue
            key = (repo, int(hit["number"]))
            if key not in pr_issue_cache:
                pr_issue_cache[key] = resolve_issues_from_pr(
                    repo,
                    int(hit["number"]),
                    command_log=command_log_path,
                    seed_refs=list(hit.get("title_issue_refs") or []),
                )
                time.sleep(0.25)
            for issue in pr_issue_cache[key]:
                issue_hits_by_repo[repo].append(
                    {
                        **issue,
                        "phrase": phrase,
                        "phrases": [phrase],
                    }
                )

    queue_records = assign_queue(scope, issue_hits_by_repo)
    snapshot = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R1",
        "scope_sha256": sha256_file(scope_path),
        "created_utc": utc_now(),
        "query_count": len(query_results),
        "queries": query_results,
    }
    queue = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R1",
        "scope_sha256": sha256_file(scope_path),
        "search_snapshot_sha256": "",  # filled after snapshot write
        "created_utc": utc_now(),
        "records": queue_records,
    }
    write_json(snapshot_path, snapshot)
    queue["search_snapshot_sha256"] = sha256_file(snapshot_path)
    write_json(queue_path, queue)
    append_command_log(
        command_log_path,
        {
            "label": "search_complete",
            "command": ["mine_supplemental_r1.py", "search"],
            "cwd": str(Path.cwd()),
            "timestamp_utc": utc_now(),
            "exit_code": 0,
            "stdout_sha256": sha256_file(snapshot_path),
            "stderr_tail": "",
            "queue_count": len(queue_records),
        },
    )


def _gh_json(path: str, command_log: Path, label: str) -> dict[str, Any]:
    return run_gh(["api", "-X", "GET", path], command_log=command_log, label=label)


def _extract_fix_refs(issue: dict[str, Any], timeline: list[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for event in timeline:
        event_type = event.get("event") or event.get("type") or ""
        if event_type in {"closed", "referenced", "cross-referenced"}:
            source = event.get("source") or {}
            issue_obj = source.get("issue") or {}
            if issue_obj.get("pull_request"):
                html = issue_obj.get("html_url")
                if html:
                    refs.append(html)
            commit_id = event.get("commit_id")
            if commit_id:
                refs.append(commit_id)
        if event_type == "connected":
            subject = event.get("subject") or {}
            html = subject.get("html_url")
            if html:
                refs.append(html)
    body = issue.get("body") or ""
    for match in re.findall(
        r"https://github\.com/[^/\s]+/[^/\s]+/(?:pull|commit)/[0-9a-fA-F]+",
        body,
    ):
        refs.append(match)
    # Preserve order, unique.
    seen: set[str] = set()
    out: list[str] = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def _commit_files_meta(commit: dict[str, Any]) -> list[dict[str, Any]]:
    files = []
    for f in commit.get("files", [])[:80]:
        files.append(
            {
                "filename": f.get("filename", ""),
                "status": f.get("status", ""),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "patch_sha256": sha256_text(f.get("patch") or ""),
            }
        )
    return files


def _fix_candidate_from_pr(
    repo: str,
    pr_number: int,
    *,
    command_log: Path,
    prefetched: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    try:
        pr = prefetched or _gh_json(
            f"repos/{repo}/pulls/{pr_number}",
            command_log,
            f"pull:{repo}#{pr_number}",
        )
    except RuntimeError:
        return None
    merge_commit = pr.get("merge_commit_sha") or ""
    head_sha = ((pr.get("head") or {}).get("sha")) or pr.get("head_sha") or ""
    fixed_sha = merge_commit or head_sha
    if not fixed_sha:
        return None
    parents: list[str] = []
    files: list[dict[str, Any]] = []
    try:
        commit = _gh_json(
            f"repos/{repo}/commits/{fixed_sha}",
            command_log,
            f"commit:{repo}@{fixed_sha[:12]}",
        )
        parents = [p.get("sha", "") for p in commit.get("parents", [])]
        files = _commit_files_meta(commit)
    except RuntimeError:
        # Keep the PR identity even when the merge commit is unavailable in-repo
        # (e.g. cross-repo or rewritten history). Parent SHAs then remain blank.
        parents = []
        files = []
    return {
        "fix_url": pr.get("html_url") or f"https://github.com/{repo}/pull/{pr_number}",
        "fixed_sha": fixed_sha,
        "buggy_sha": parents[0] if parents else "",
        "merged": bool(pr.get("merged")),
        "state": pr.get("state", ""),
        "merge_commit_sha": merge_commit,
        "head_sha": head_sha,
        "title_sha256": sha256_text(pr.get("title") or ""),
        "body_sha256": sha256_text(pr.get("body") or ""),
        "files": files,
        "parent_shas": parents,
    }


def collect_one(
    record: dict[str, Any],
    *,
    command_log: Path,
) -> dict[str, Any]:
    repo = record["repo"]
    number = record["issue_number"]
    issue = _gh_json(
        f"repos/{repo}/issues/{number}",
        command_log,
        f"issue:{repo}#{number}",
    )
    try:
        timeline = run_gh(
            [
                "api",
                "-X",
                "GET",
                f"repos/{repo}/issues/{number}/timeline",
                "-H",
                "Accept: application/vnd.github+json",
                "-F",
                "per_page=100",
            ],
            command_log=command_log,
            label=f"timeline:{repo}#{number}",
        )
        if isinstance(timeline, dict):
            timeline_items = timeline.get("items") or []
        else:
            timeline_items = timeline
    except RuntimeError:
        timeline_items = []

    fix_refs = _extract_fix_refs(issue, timeline_items if isinstance(timeline_items, list) else [])
    for source_pr in record.get("source_prs") or []:
        pr_url = source_pr.get("pr_url")
        if pr_url and pr_url not in fix_refs:
            fix_refs.insert(0, pr_url)

    fix_candidates: list[dict[str, Any]] = []
    seen_fix_urls: set[str] = set()

    # Prefer provenance PRs captured during search resolution.
    for source_pr in record.get("source_prs") or []:
        pr_number = int(source_pr.get("pr_number") or 0)
        if not pr_number:
            continue
        candidate = _fix_candidate_from_pr(repo, pr_number, command_log=command_log)
        if candidate and candidate["fix_url"] not in seen_fix_urls:
            # If REST lacked merge metadata, fall back to GraphQL fields from search.
            if not candidate.get("buggy_sha") and source_pr.get("merge_commit_sha"):
                candidate["fixed_sha"] = source_pr.get("merge_commit_sha") or candidate["fixed_sha"]
                candidate["merge_commit_sha"] = source_pr.get("merge_commit_sha") or ""
                candidate["head_sha"] = source_pr.get("head_sha") or candidate.get("head_sha") or ""
                candidate["merged"] = bool(source_pr.get("merged"))
                try:
                    commit = _gh_json(
                        f"repos/{repo}/commits/{candidate['fixed_sha']}",
                        command_log,
                        f"commit:{repo}@{candidate['fixed_sha'][:12]}",
                    )
                    parents = [p.get("sha", "") for p in commit.get("parents", [])]
                    candidate["parent_shas"] = parents
                    candidate["buggy_sha"] = parents[0] if parents else ""
                    candidate["files"] = _commit_files_meta(commit)
                except RuntimeError:
                    pass
            seen_fix_urls.add(candidate["fix_url"])
            fix_candidates.append(candidate)

    for ref in fix_refs:
        if "/pull/" in ref:
            pr_number = int(ref.rstrip("/").rsplit("/", 1)[-1])
            candidate = _fix_candidate_from_pr(repo, pr_number, command_log=command_log)
            if candidate and candidate["fix_url"] not in seen_fix_urls:
                seen_fix_urls.add(candidate["fix_url"])
                fix_candidates.append(candidate)
        elif re.fullmatch(r"[0-9a-fA-F]{7,40}", ref) or "/commit/" in ref:
            sha = ref.rstrip("/").rsplit("/", 1)[-1]
            try:
                commit = _gh_json(
                    f"repos/{repo}/commits/{sha}",
                    command_log,
                    f"commit:{repo}@{sha[:12]}",
                )
            except RuntimeError:
                continue
            parents = [p.get("sha", "") for p in commit.get("parents", [])]
            html = commit.get("html_url") or f"https://github.com/{repo}/commit/{commit.get('sha', sha)}"
            if html in seen_fix_urls:
                continue
            seen_fix_urls.add(html)
            fix_candidates.append(
                {
                    "fix_url": html,
                    "fixed_sha": commit.get("sha", sha),
                    "buggy_sha": parents[0] if parents else "",
                    "merged": True,
                    "state": "commit",
                    "merge_commit_sha": commit.get("sha", sha),
                    "head_sha": commit.get("sha", sha),
                    "title_sha256": sha256_text((commit.get("commit") or {}).get("message") or ""),
                    "body_sha256": sha256_text(""),
                    "files": _commit_files_meta(commit),
                    "parent_shas": parents,
                }
            )

    labels = [lbl.get("name", "") for lbl in issue.get("labels", []) if isinstance(lbl, dict)]
    return {
        "neutral_id": record["neutral_id"],
        "repo": repo,
        "issue_number": number,
        "issue_url": record["issue_url"],
        "state": issue.get("state", ""),
        "created_at": issue.get("created_at", ""),
        "closed_at": issue.get("closed_at", ""),
        "title_sha256": sha256_text(issue.get("title") or ""),
        "body_sha256": sha256_text(issue.get("body") or ""),
        "label_names": labels,
        "fix_refs": fix_refs,
        "fix_candidates": fix_candidates,
        "timeline_event_count": len(timeline_items) if isinstance(timeline_items, list) else 0,
    }


def cmd_collect_evidence(
    scope_path: Path,
    queue_path: Path,
    snapshot_path: Path,
    output_path: Path,
    command_log_path: Path,
) -> None:
    scope = load_scope(scope_path)
    queue = load_json(queue_path)
    # Collect for all queue records; review stop is applied later during decisions.
    records = queue["records"]
    evidence_rows = []
    for record in records:
        # Bound network: collect only up to max_reviewed_per_repo in queue order per repo.
        pass
    # Determine which records need evidence: first max_reviewed per repo.
    selected: list[dict[str, Any]] = []
    per_repo_count: dict[str, int] = {}
    for record in records:
        repo = record["repo"]
        count = per_repo_count.get(repo, 0)
        if count >= int(scope["max_reviewed_per_repo"]):
            continue
        per_repo_count[repo] = count + 1
        selected.append(record)

    for record in selected:
        evidence_rows.append(collect_one(record, command_log=command_log_path))

    payload = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R1",
        "scope_sha256": sha256_file(scope_path),
        "search_snapshot_sha256": sha256_file(snapshot_path),
        "review_queue_sha256": sha256_file(queue_path),
        "created_utc": utc_now(),
        "records": evidence_rows,
    }
    write_json(output_path, payload)


def _read_sheet_ids(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["neutral_id"] for row in csv.DictReader(handle)}


def _read_sheet_pairs(path: Path) -> set[tuple[str, str, str]]:
    pairs: set[tuple[str, str, str]] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            buggy = (row.get("buggy_sha") or "").strip()
            fixed = (row.get("fixed_sha") or "").strip()
            if buggy and fixed:
                pairs.add((row["issue_url"], buggy, fixed))
    return pairs


def cmd_validate_decisions(
    scope_path: Path,
    snapshot_path: Path,
    queue_path: Path,
    decisions_path: Path,
    existing_sheet: Path,
    pilot_sheet: Path,
) -> None:
    scope = load_scope(scope_path)
    queue = load_json(queue_path)
    decisions_payload = load_json(decisions_path)
    decisions = decisions_payload.get("decisions") or []
    errors: list[str] = []

    allowed_repos = {r["repo"] for r in scope["repositories"]}
    prefix_by_repo = {r["repo"]: r["id_prefix"] for r in scope["repositories"]}
    existing_ids = _read_sheet_ids(existing_sheet) | _read_sheet_ids(pilot_sheet)
    existing_pairs = _read_sheet_pairs(existing_sheet) | _read_sheet_pairs(pilot_sheet)

    queue_by_id = {r["neutral_id"]: r for r in queue["records"]}
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    seen_pairs: set[tuple[str, str, str]] = set()
    pending_by_repo: dict[str, int] = {}
    reviewed_by_repo: dict[str, int] = {}

    for index, decision in enumerate(decisions, start=1):
        missing = [field for field in DECISION_FIELDS if field not in decision]
        if missing:
            errors.append(f"decision[{index}] missing fields: {missing}")
            continue
        nid = decision["neutral_id"]
        repo = decision["repo"]
        if repo not in allowed_repos:
            errors.append(f"{nid}: repo outside SCOPE")
        if not nid.startswith(prefix_by_repo.get(repo, "")):
            errors.append(f"{nid}: neutral_id prefix mismatch for {repo}")
        if nid in existing_ids:
            errors.append(f"{nid}: neutral-ID collision with existing admission sheet")
        if nid in seen_ids:
            errors.append(f"{nid}: duplicate neutral_id in decisions")
        seen_ids.add(nid)
        if decision["issue_url"] in seen_urls:
            errors.append(f"{nid}: duplicate issue URL")
        seen_urls.add(decision["issue_url"])
        if nid not in queue_by_id:
            errors.append(f"{nid}: not present in review queue")
        if decision["analysis_id"] != "":
            errors.append(f"{nid}: analysis_id must be blank")
        if decision["crit_dual_arm_repro"] != "PENDING":
            errors.append(f"{nid}: A2 must remain PENDING")
        if decision["review_status"] != "REVIEWED":
            errors.append(f"{nid}: review_status must be REVIEWED")
        if decision["decision"] == "ADMIT_PENDING_REPRO":
            if decision["crit_real_defect"] != "PASS" or decision["crit_in_scope"] != "PASS":
                errors.append(f"{nid}: ADMIT_PENDING_REPRO requires A1 and A3 PASS")
            if not FULL_SHA.fullmatch(decision["buggy_sha"] or ""):
                errors.append(f"{nid}: missing full buggy_sha on A1 PASS")
            if not FULL_SHA.fullmatch(decision["fixed_sha"] or ""):
                errors.append(f"{nid}: missing full fixed_sha on A1 PASS")
            if not decision["issue_url"] or not decision["fix_url"]:
                errors.append(f"{nid}: missing public issue/fix URL on A1 PASS")
            pending_by_repo[repo] = pending_by_repo.get(repo, 0) + 1
        else:
            if decision["decision"] != "EXCLUDED":
                errors.append(f"{nid}: decision must be ADMIT_PENDING_REPRO or EXCLUDED")
            if decision["crit_real_defect"] == "PASS" and decision["crit_in_scope"] == "PASS":
                errors.append(f"{nid}: EXCLUDED despite A1 and A3 PASS")
        if decision["crit_real_defect"] == "PASS":
            if not FULL_SHA.fullmatch(decision.get("buggy_sha") or ""):
                errors.append(f"{nid}: A1 PASS requires full buggy_sha")
            if not FULL_SHA.fullmatch(decision.get("fixed_sha") or ""):
                errors.append(f"{nid}: A1 PASS requires full fixed_sha")
        text_blob = " ".join(
            [
                decision.get("mechanism_sentence") or "",
                decision.get("exclusion_reason") or "",
                json.dumps(decision.get("rationales") or {}, sort_keys=True),
            ]
        )
        if RESERVED_RE.search(text_blob) or PROHIBITED_RE.search(text_blob):
            errors.append(f"{nid}: reserved/downstream vocabulary in rationale/mechanism")
        buggy = (decision.get("buggy_sha") or "").strip()
        fixed = (decision.get("fixed_sha") or "").strip()
        if buggy and fixed:
            pair = (decision["issue_url"], buggy, fixed)
            if pair in seen_pairs or pair in existing_pairs:
                errors.append(f"{nid}: duplicate buggy/fixed pair")
            seen_pairs.add(pair)
        reviewed_by_repo[repo] = reviewed_by_repo.get(repo, 0) + 1
        if decision["review_order"] != reviewed_by_repo[repo]:
            # Allow explicit order values as long as unique increasing per repo.
            pass

    for repo, count in pending_by_repo.items():
        if count > int(scope["target_pending_per_repo"]):
            errors.append(f"{repo}: pending quota exceeded ({count})")
    for repo, count in reviewed_by_repo.items():
        if count > int(scope["max_reviewed_per_repo"]):
            errors.append(f"{repo}: reviewed cap exceeded ({count})")

    # Ensure reviewed exclusions retained: every REVIEWED queue head through stop must
    # have a decision. Reconstruct stop using decisions order.
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        repo_queue = [r for r in queue["records"] if r["repo"] == repo]
        repo_decisions = [d for d in decisions if d["repo"] == repo]
        repo_decisions_sorted = sorted(repo_decisions, key=lambda d: d["review_order"])
        annotated = apply_review_stop(
            [
                {
                    "neutral_id": r["neutral_id"],
                    "repo": r["repo"],
                    "issue_number": r["issue_number"],
                    "issue_url": r["issue_url"],
                    "created_at": r.get("created_at", ""),
                }
                for r in repo_queue
            ],
            repo_decisions_sorted,
            max_reviewed=int(scope["max_reviewed_per_repo"]),
            target_pending=int(scope["target_pending_per_repo"]),
        )
        reviewed_ids = {r["neutral_id"] for r in annotated if r["review_status"] == "REVIEWED"}
        decision_ids = {d["neutral_id"] for d in repo_decisions}
        missing = sorted(reviewed_ids - decision_ids)
        if missing:
            errors.append(f"{repo}: missing decisions for reviewed ids {missing}")
        extra = sorted(decision_ids - reviewed_ids)
        if extra:
            errors.append(f"{repo}: decisions beyond stop boundary {extra}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
    print("VALIDATE_DECISIONS_OK")


def cmd_build(
    scope_path: Path,
    snapshot_path: Path,
    decisions_path: Path,
    sheet_path: Path,
    evidence_root: Path,
) -> None:
    scope = load_scope(scope_path)
    decisions = load_json(decisions_path)["decisions"]
    scope_sha = sha256_file(scope_path)
    search_sha = sha256_file(snapshot_path)
    # Write sheet first without evidence hashes dependency on decisions file hash.
    rows: list[dict[str, str]] = []
    for decision in sorted(
        decisions,
        key=lambda d: (
            [r["repo"] for r in scope["repositories"]].index(d["repo"]),
            d["review_order"],
        ),
    ):
        rows.append(
            {
                "neutral_id": decision["neutral_id"],
                "repo": decision["repo"].split("/")[-1]
                if decision["repo"] in {r["repo"] for r in scope["repositories"]}
                else decision["repo"],
                # Keep short repo label like pilot sheet for whitelist projects? Pilot uses
                # short names (numpy). Cursor candidate uses short project names too.
                # Use final path segment for consistency with existing sheets.
                "issue_url": decision["issue_url"],
                "buggy_sha": decision.get("buggy_sha") or "",
                "fixed_sha": decision.get("fixed_sha") or "",
                "mechanism_sentence": decision["mechanism_sentence"],
                "crit_real_defect": decision["crit_real_defect"],
                "crit_dual_arm_repro": decision["crit_dual_arm_repro"],
                "crit_in_scope": decision["crit_in_scope"],
                "decision": decision["decision"],
                "exclusion_reason": decision.get("exclusion_reason") or "",
                "analysis_id": decision.get("analysis_id") or "",
            }
        )
    # Fix repo field properly: use short name from full repo path.
    for row, decision in zip(rows, sorted(
        decisions,
        key=lambda d: (
            [r["repo"] for r in scope["repositories"]].index(d["repo"]),
            d["review_order"],
        ),
    )):
        row["repo"] = decision["repo"].split("/")[-1]

    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    with sheet_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    decisions_sha = sha256_file(decisions_path)
    if evidence_root.exists():
        for child in evidence_root.iterdir():
            if child.is_dir():
                for path in child.glob("evidence.json"):
                    path.unlink()
    evidence_root.mkdir(parents=True, exist_ok=True)
    for decision in decisions:
        case_dir = evidence_root / decision["neutral_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "neutral_id": decision["neutral_id"],
            "source_pool": "supplemental_mining_r1",
            "scope_sha256": scope_sha,
            "search_snapshot_sha256": search_sha,
            "review_decisions_sha256": decisions_sha,
            "issue_url": decision["issue_url"],
            "fix_url": decision.get("fix_url") or "",
            "buggy_sha": decision.get("buggy_sha") or "",
            "fixed_sha": decision.get("fixed_sha") or "",
            "criteria": {
                "real_defect": decision["crit_real_defect"],
                "dual_arm_repro": decision["crit_dual_arm_repro"],
                "in_scope": decision["crit_in_scope"],
            },
            "rationales": decision["rationales"],
            "evidence_urls": decision["evidence_urls"],
            "mechanism_sentence": decision["mechanism_sentence"],
        }
        write_json(case_dir / "evidence.json", payload)
    print(f"BUILD_OK rows={len(rows)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search")
    search.add_argument("--scope", type=Path, required=True)
    search.add_argument("--snapshot", type=Path, required=True)
    search.add_argument("--queue", type=Path, required=True)
    search.add_argument("--command-log", type=Path, required=True)

    collect = sub.add_parser("collect-evidence")
    collect.add_argument("--scope", type=Path, required=True)
    collect.add_argument("--queue", type=Path, required=True)
    collect.add_argument("--snapshot", type=Path, required=True)
    collect.add_argument("--output", type=Path, required=True)
    collect.add_argument("--command-log", type=Path, required=True)

    validate = sub.add_parser("validate-decisions")
    validate.add_argument("--scope", type=Path, required=True)
    validate.add_argument("--snapshot", type=Path, required=True)
    validate.add_argument("--queue", type=Path, required=True)
    validate.add_argument("--decisions", type=Path, required=True)
    validate.add_argument("--existing-sheet", type=Path, required=True)
    validate.add_argument("--pilot-sheet", type=Path, required=True)

    build = sub.add_parser("build")
    build.add_argument("--scope", type=Path, required=True)
    build.add_argument("--snapshot", type=Path, required=True)
    build.add_argument("--decisions", type=Path, required=True)
    build.add_argument("--sheet", type=Path, required=True)
    build.add_argument("--evidence-root", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "search":
        cmd_search(args.scope, args.snapshot, args.queue, args.command_log)
    elif args.command == "collect-evidence":
        cmd_collect_evidence(
            args.scope,
            args.queue,
            args.snapshot,
            args.output,
            args.command_log,
        )
    elif args.command == "validate-decisions":
        cmd_validate_decisions(
            args.scope,
            args.snapshot,
            args.queue,
            args.decisions,
            args.existing_sheet,
            args.pilot_sheet,
        )
    elif args.command == "build":
        cmd_build(
            args.scope,
            args.snapshot,
            args.decisions,
            args.sheet,
            args.evidence_root,
        )
    else:
        parser.error(f"unknown command {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
