#!/usr/bin/env python3
"""Validate a C2 admission candidate without freezing it."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NoReturn


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
FULL_SHA = re.compile(r"[0-9a-f]{40}")
NEUTRAL_ID = re.compile(r"EXT-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9]{2}")
SOURCE_HASH = re.compile(r"[0-9a-f]{64}")
PROHIBITED_PREFIX = re.compile(r"EXT-[A-Fa-f]-")
REAL_VALUES = {"PASS", "FAIL"}
DUAL_VALUES = {"PENDING", "PASS", "REPRO_FAILED"}
SCOPE_VALUES = {"PASS", "FAIL"}
DECISION_VALUES = {"ADMIT_PENDING_REPRO", "EXCLUDED"}
PROHIBITED_TEXT = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|\bkill\b|\bfiber\b|\boperator\b|prediction)"
)
PUBLIC_URL = re.compile(r"https?://[^\s]+")
EVIDENCE_KEYS = {
    "neutral_id",
    "source_pool",
    "source_index",
    "source_manifest_sha256",
    "issue_url",
    "fix_url",
    "buggy_sha",
    "fixed_sha",
    "criteria",
    "rationales",
    "evidence_urls",
    "mechanism_sentence",
    "dual_arm_evidence",
}


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_sheet(path: Path, *, scan_prohibited: bool = False) -> list[dict[str, str]]:
    if not path.is_file():
        fail(f"sheet does not exist: {path}")
    raw = path.read_text(encoding="utf-8")
    if scan_prohibited and PROHIBITED_TEXT.search(raw):
        fail("prohibited downstream vocabulary in sheet")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            fail(f"sheet header must be exactly {','.join(HEADER)}")
        rows = list(reader)
    if any(None in row for row in rows):
        fail("row width does not match exact header")
    return rows


def validate_sha(value: str, field: str, neutral_id: str, *, required: bool) -> None:
    if not value:
        if required:
            fail(f"{neutral_id}: {field} is required")
        return
    if FULL_SHA.fullmatch(value) is None:
        fail(f"{neutral_id}: {field} must be a full 40-character commit")


def expected_decision(row: dict[str, str]) -> str:
    if (
        row["crit_real_defect"] == "PASS"
        and row["crit_in_scope"] == "PASS"
        and row["crit_dual_arm_repro"] != "REPRO_FAILED"
    ):
        return "ADMIT_PENDING_REPRO"
    return "EXCLUDED"


def validate_candidate_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != 64:
        fail(f"candidate sheet must contain exactly 64 rows, found {len(rows)}")
    ids = [row["neutral_id"] for row in rows]
    if len(ids) != len(set(ids)):
        fail("candidate sheet contains duplicate neutral_id values")

    for row in rows:
        neutral_id = row["neutral_id"]
        if PROHIBITED_PREFIX.match(neutral_id):
            fail(f"{neutral_id}: neutral_id encodes a prohibited category prefix")
        if NEUTRAL_ID.fullmatch(neutral_id) is None:
            fail(f"{neutral_id}: neutral_id must match EXT-<repo>-<NN>")
        if row["analysis_id"] != "":
            fail(f"{neutral_id}: analysis_id must be blank")
        if row["crit_real_defect"] not in REAL_VALUES:
            fail(f"{neutral_id}: invalid crit_real_defect")
        if row["crit_dual_arm_repro"] not in DUAL_VALUES:
            fail(f"{neutral_id}: invalid crit_dual_arm_repro")
        if row["crit_in_scope"] not in SCOPE_VALUES:
            fail(f"{neutral_id}: invalid crit_in_scope")
        if row["decision"] not in DECISION_VALUES:
            fail(f"{neutral_id}: invalid decision")
        if row["decision"] != expected_decision(row):
            fail(f"{neutral_id}: decision is inconsistent with the three criteria")
        if row["decision"] == "EXCLUDED" and not row["exclusion_reason"].strip():
            fail(f"{neutral_id}: excluded rows require an exclusion_reason")
        if not row["mechanism_sentence"].strip():
            fail(f"{neutral_id}: mechanism_sentence must not be blank")

        immutable_required = row["crit_real_defect"] == "PASS"
        validate_sha(row["buggy_sha"], "buggy_sha", neutral_id, required=immutable_required)
        validate_sha(row["fixed_sha"], "fixed_sha", neutral_id, required=immutable_required)
        if row["crit_dual_arm_repro"] == "PASS" and not (
            FULL_SHA.fullmatch(row["buggy_sha"]) and FULL_SHA.fullmatch(row["fixed_sha"])
        ):
            fail(f"{neutral_id}: dual-arm PASS requires immutable buggy and fixed commits")


def validate_evidence(
    rows: list[dict[str, str]], evidence_root: Path
) -> None:
    if not evidence_root.is_dir():
        fail(f"evidence root does not exist: {evidence_root}")
    row_by_id = {row["neutral_id"]: row for row in rows}
    actual_dirs = {path.name for path in evidence_root.iterdir() if path.is_dir()}
    root_files = [path.name for path in evidence_root.iterdir() if not path.is_dir()]
    if root_files:
        fail(f"evidence root must contain only case directories: {sorted(root_files)}")
    if actual_dirs != set(row_by_id):
        missing = sorted(set(row_by_id) - actual_dirs)
        extra = sorted(actual_dirs - set(row_by_id))
        fail(f"evidence directory identity mismatch; missing={missing}, extra={extra}")

    source_indices: list[int] = []
    source_hashes: set[str] = set()
    for expected_index, row in enumerate(rows, start=1):
        neutral_id = row["neutral_id"]
        case_dir = evidence_root / neutral_id
        case_entries = {path.name for path in case_dir.iterdir()}
        if case_entries != {"evidence.json"}:
            fail(f"{neutral_id}: case directory must contain only evidence.json")
        path = case_dir / "evidence.json"
        if not path.is_file():
            fail(f"{neutral_id}: missing evidence.json")
        raw = path.read_text(encoding="utf-8")
        if PROHIBITED_TEXT.search(raw):
            fail(f"{neutral_id}: prohibited downstream vocabulary in evidence")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"{neutral_id}: invalid evidence JSON: {exc}")
        if payload.get("neutral_id") != neutral_id:
            fail(f"{neutral_id}: evidence neutral_id mismatch")
        if not isinstance(payload, dict) or not set(payload).issubset(EVIDENCE_KEYS):
            fail(f"{neutral_id}: evidence contains fields outside the admission allowlist")
        if payload.get("source_pool") != "defect4mr_64":
            fail(f"{neutral_id}: source_pool must be defect4mr_64")
        source_index = payload.get("source_index")
        if not isinstance(source_index, int):
            fail(f"{neutral_id}: source_index must be an integer")
        source_indices.append(source_index)
        if source_index != expected_index:
            fail(f"{neutral_id}: source_index must match candidate row position")
        source_hash = str(payload.get("source_manifest_sha256", ""))
        if SOURCE_HASH.fullmatch(source_hash) is None:
            fail(f"{neutral_id}: source_manifest_sha256 must be a SHA256")
        source_hashes.add(source_hash)
        for key in ("issue_url", "buggy_sha", "fixed_sha"):
            if payload.get(key, "") != row[key]:
                fail(f"{neutral_id}: evidence {key} does not match sheet")
        criteria = payload.get("criteria")
        expected = {
            "real_defect": row["crit_real_defect"],
            "dual_arm_repro": row["crit_dual_arm_repro"],
            "in_scope": row["crit_in_scope"],
        }
        if criteria != expected:
            fail(f"{neutral_id}: evidence criteria do not match sheet")
        if payload.get("mechanism_sentence") != row["mechanism_sentence"]:
            fail(f"{neutral_id}: evidence mechanism_sentence does not match sheet")
        rationales = payload.get("rationales")
        if not isinstance(rationales, dict) or set(rationales) != set(expected):
            fail(f"{neutral_id}: evidence requires one rationale per criterion")
        if not all(isinstance(value, str) and value.strip() for value in rationales.values()):
            fail(f"{neutral_id}: evidence rationales must be nonblank")
        if row["crit_real_defect"] == "PASS" and not payload.get("fix_url"):
            fail(f"{neutral_id}: real-defect PASS requires a public fix URL")
        evidence_urls = payload.get("evidence_urls")
        if not isinstance(evidence_urls, list) or not all(
            isinstance(url, str) and PUBLIC_URL.fullmatch(url) for url in evidence_urls
        ):
            fail(f"{neutral_id}: evidence_urls must contain public HTTP(S) URLs")
        for url_key in ("issue_url", "fix_url"):
            url = payload.get(url_key, "")
            if url and (PUBLIC_URL.fullmatch(url) is None or url not in evidence_urls):
                fail(f"{neutral_id}: {url_key} must be a public URL included in evidence_urls")
        fixed_sha = payload.get("fixed_sha", "")
        fix_url = payload.get("fix_url", "")
        if fixed_sha and fix_url and fixed_sha not in fix_url:
            fail(f"{neutral_id}: fix_url must bind the recorded fixed_sha")
        if row["crit_dual_arm_repro"] == "PASS":
            dual = payload.get("dual_arm_evidence")
            required = {"buggy_url", "fixed_url", "trigger_url", "buggy_sha", "fixed_sha"}
            if not isinstance(dual, dict) or set(dual) != required:
                fail(f"{neutral_id}: dual-arm PASS requires public execution evidence for both arms")
            if dual["buggy_sha"] != row["buggy_sha"] or dual["fixed_sha"] != row["fixed_sha"]:
                fail(f"{neutral_id}: dual-arm execution evidence must bind both recorded commits")
            if not all(PUBLIC_URL.fullmatch(dual[key]) for key in ("buggy_url", "fixed_url", "trigger_url")):
                fail(f"{neutral_id}: dual-arm execution evidence URLs must be public HTTP(S) URLs")
        elif "dual_arm_evidence" in payload:
            fail(f"{neutral_id}: dual_arm_evidence is forbidden unless the criterion is PASS")

    if sorted(source_indices) != list(range(1, 65)):
        fail("evidence source_index values must cover 1..64 exactly once")
    if len(source_hashes) != 1:
        fail("all evidence must bind the same source manifest")
    source_manifest = evidence_root.parent / "defect4mr_import" / "candidates_sanitized.json"
    if not source_manifest.is_file():
        fail("sanitized source manifest is required")
    actual_hash = hashlib.sha256(source_manifest.read_bytes()).hexdigest()
    if source_hashes != {actual_hash}:
        fail("evidence source_manifest_sha256 does not match candidates_sanitized.json")


def validate_supplemental_pilot(path: Path, candidate_ids: set[str]) -> None:
    rows = read_sheet(path)
    if len(rows) != 9:
        fail(f"supplemental pilot sheet must contain exactly 9 rows, found {len(rows)}")
    ids = [row["neutral_id"] for row in rows]
    if len(ids) != len(set(ids)):
        fail("supplemental pilot contains duplicate neutral_id values")
    if candidate_ids.intersection(ids):
        fail("supplemental pilot IDs overlap the Defect4MR 64 candidate")
    if any(row["analysis_id"] for row in rows):
        fail("supplemental pilot analysis_id must be blank")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--supplemental-sheet", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sheet = args.sheet.resolve()
    evidence_root = (
        args.evidence_root.resolve()
        if args.evidence_root
        else sheet.parent / "admission_evidence"
    )
    supplemental = (
        args.supplemental_sheet.resolve()
        if args.supplemental_sheet
        else sheet.parent / "admission_sheet.csv"
    )
    rows = read_sheet(sheet, scan_prohibited=True)
    validate_candidate_rows(rows)
    validate_evidence(rows, evidence_root)
    validate_supplemental_pilot(supplemental, {row["neutral_id"] for row in rows})
    print(
        "PASS: 64 Defect4MR candidate rows, 64 evidence records, "
        "and 9 supplemental pilot rows are structurally valid and separate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
