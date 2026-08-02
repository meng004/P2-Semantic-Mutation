#!/usr/bin/env python3
"""Admission checker for supplemental mining R1 candidate payload."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, NoReturn

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

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
RESERVED_RE = re.compile(
    r"(?i)(^|[^A-Za-z0-9_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)"
    r"([^A-Za-z0-9_]|$)"
)
PROHIBITED_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b)"
)

EVIDENCE_REQUIRED = {
    "neutral_id",
    "source_pool",
    "scope_sha256",
    "search_snapshot_sha256",
    "review_decisions_sha256",
    "issue_url",
    "fix_url",
    "buggy_sha",
    "fixed_sha",
    "criteria",
    "rationales",
    "evidence_urls",
    "mechanism_sentence",
}


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sheet(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != HEADER:
            fail(f"sheet header must be exactly {','.join(HEADER)}")
        return list(reader)


def text_blob_for_row(row: dict[str, str], decision: dict[str, Any] | None = None) -> str:
    parts = [
        row.get("mechanism_sentence", ""),
        row.get("exclusion_reason", ""),
    ]
    if decision:
        parts.append(json.dumps(decision.get("rationales") or {}, sort_keys=True))
        parts.append(decision.get("mechanism_sentence") or "")
        parts.append(decision.get("exclusion_reason") or "")
    return "\n".join(parts)


def verify_input_hashes(scope: dict[str, Any], *, fixture_root: Path | None) -> None:
    root = fixture_root if fixture_root is not None else Path.cwd()
    for rel, expected in scope.get("input_sha256", {}).items():
        path = Path(rel)
        if not path.is_absolute():
            path = root / rel
        if not path.is_file():
            fail(f"missing immutable input for hash check: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            fail(f"changed input hash for {rel}: expected {expected}, got {actual}")
    if scope.get("baseline_commit") != "0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a":
        fail("baseline_commit mismatch in SCOPE.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--existing-sheet", type=Path, required=True)
    parser.add_argument("--pilot-sheet", type=Path, required=True)
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=None,
        help="optional root for resolving SCOPE input_sha256 paths in tests",
    )
    args = parser.parse_args()

    scope = load_json(args.scope)
    snapshot = load_json(args.snapshot)
    decisions_payload = load_json(args.decisions)
    decisions = decisions_payload.get("decisions") or []
    rows = read_sheet(args.sheet)
    existing = read_sheet(args.existing_sheet)
    pilot = read_sheet(args.pilot_sheet)

    verify_input_hashes(scope, fixture_root=args.fixture_root)

    allowed_repos = {r["repo"] for r in scope["repositories"]}
    allowed_short = {r["repo"].split("/")[-1] for r in scope["repositories"]}
    phrases = set(scope["phrases"])
    prefix_by_repo = {r["repo"]: r["id_prefix"] for r in scope["repositories"]}
    short_to_full = {r["repo"].split("/")[-1]: r["repo"] for r in scope["repositories"]}

    for query in snapshot.get("queries", []):
        if query.get("repo") not in allowed_repos:
            fail(f"snapshot repository outside SCOPE: {query.get('repo')}")
        if query.get("phrase") not in phrases:
            fail(f"snapshot phrase outside SCOPE: {query.get('phrase')}")

    existing_ids = {r["neutral_id"] for r in existing} | {r["neutral_id"] for r in pilot}
    existing_urls = {r["issue_url"] for r in existing} | {r["issue_url"] for r in pilot}
    existing_pairs = {
        (r["issue_url"], r["buggy_sha"], r["fixed_sha"])
        for r in existing + pilot
        if r.get("buggy_sha") and r.get("fixed_sha")
    }

    decision_by_id = {d["neutral_id"]: d for d in decisions}
    if len(decision_by_id) != len(decisions):
        fail("duplicate neutral_id in decisions")
    if {r["neutral_id"] for r in rows} != set(decision_by_id):
        fail("sheet rows and decisions are not 1:1")

    scope_sha = sha256_file(args.scope)
    search_sha = sha256_file(args.snapshot)
    decisions_sha = sha256_file(args.decisions)

    pending_by_repo: Counter[str] = Counter()
    reviewed_by_repo: Counter[str] = Counter()
    excluded_by_repo: Counter[str] = Counter()
    seen_urls: set[str] = set()
    seen_pairs: set[tuple[str, str, str]] = set()

    for row in rows:
        nid = row["neutral_id"]
        decision = decision_by_id[nid]
        repo_short = row["repo"]
        repo_full = decision["repo"]
        if repo_full not in allowed_repos:
            fail(f"{nid}: repository outside SCOPE")
        if repo_short not in allowed_short and repo_short not in allowed_repos:
            fail(f"{nid}: sheet repo not in SCOPE")
        if not nid.startswith(prefix_by_repo[repo_full]):
            fail(f"{nid}: neutral_id prefix mismatch")
        if nid in existing_ids:
            fail(f"{nid}: neutral-ID collision with existing admission sheet")
        if row["issue_url"] in existing_urls or row["issue_url"] in seen_urls:
            fail(f"{nid}: duplicate issue URL across pools")
        seen_urls.add(row["issue_url"])

        if row["crit_dual_arm_repro"] != "PENDING" or decision["crit_dual_arm_repro"] != "PENDING":
            fail(f"{nid}: A2 must remain PENDING")
        if row["analysis_id"] != "" or decision.get("analysis_id") != "":
            fail(f"{nid}: analysis_id must be blank")

        if row["decision"] == "ADMIT_PENDING_REPRO":
            if row["crit_real_defect"] != "PASS" or row["crit_in_scope"] != "PASS":
                fail(f"{nid}: ADMIT_PENDING_REPRO unless A1 and A3 both PASS")
            if not FULL_SHA.fullmatch(row["buggy_sha"] or ""):
                fail(f"{nid}: buggy_sha must be a full 40-character commit")
            if not FULL_SHA.fullmatch(row["fixed_sha"] or ""):
                fail(f"{nid}: fixed_sha must be a full 40-character commit")
            if not row["issue_url"] or not decision.get("fix_url"):
                fail(f"{nid}: missing public issue and fix URLs on an A1 PASS row")
            pending_by_repo[repo_full] += 1
        elif row["decision"] == "EXCLUDED":
            excluded_by_repo[repo_full] += 1
        else:
            fail(f"{nid}: invalid decision")

        if row["crit_real_defect"] == "PASS":
            if not FULL_SHA.fullmatch(row["buggy_sha"] or "") or not FULL_SHA.fullmatch(
                row["fixed_sha"] or ""
            ):
                fail(f"{nid}: missing full buggy/fixed SHAs on an A1 PASS row")

        blob = text_blob_for_row(row, decision)
        if RESERVED_RE.search(blob):
            fail(f"{nid}: reserved vocabulary in mechanism/rationale")
        if PROHIBITED_RE.search(blob):
            fail(f"{nid}: prohibited downstream vocabulary in mechanism/rationale")

        buggy = (row.get("buggy_sha") or "").strip()
        fixed = (row.get("fixed_sha") or "").strip()
        if buggy and fixed:
            pair = (row["issue_url"], buggy, fixed)
            if pair in existing_pairs or pair in seen_pairs:
                fail(f"{nid}: duplicate nonblank buggy/fixed pair across any pool")
            seen_pairs.add(pair)

        evidence_path = args.evidence_root / nid / "evidence.json"
        if not evidence_path.is_file():
            fail(f"{nid}: sheet row without a matching evidence record")
        payload = load_json(evidence_path)
        if not EVIDENCE_REQUIRED.issubset(set(payload)):
            fail(f"{nid}: evidence record missing required keys")
        if payload.get("source_pool") != "supplemental_mining_r1":
            fail(f"{nid}: source_pool must be supplemental_mining_r1")
        if payload.get("scope_sha256") != scope_sha:
            fail(f"{nid}: evidence scope hash mismatch")
        if payload.get("search_snapshot_sha256") != search_sha:
            fail(f"{nid}: evidence search hash mismatch")
        if payload.get("review_decisions_sha256") != decisions_sha:
            fail(f"{nid}: evidence decision hash mismatch")
        reviewed_by_repo[repo_full] += 1

    for repo, count in pending_by_repo.items():
        if count > int(scope["target_pending_per_repo"]):
            fail(f"{repo}: more than five pending rows ({count})")
    for repo, count in reviewed_by_repo.items():
        if count > int(scope["max_reviewed_per_repo"]):
            fail(f"{repo}: more than 20 reviewed rows ({count})")

    # Loss of reviewed exclusion: every decision must appear in sheet.
    if len(rows) != len(decisions):
        fail("loss of reviewed exclusion: sheet/decision count mismatch")

    searched = Counter()
    for query in snapshot.get("queries", []):
        searched[query.get("repo")] += int(query.get("returned") or 0)

    print("PASS: supplemental mining R1 admission structural check")
    print(
        json.dumps(
            {
                "searched_hits": dict(searched),
                "reviewed": dict(reviewed_by_repo),
                "pending": dict(pending_by_repo),
                "excluded": dict(excluded_by_repo),
                "rows": len(rows),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
