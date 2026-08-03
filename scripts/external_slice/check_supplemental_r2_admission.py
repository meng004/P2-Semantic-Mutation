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
        if len(dreviews) > max_reviewed:
            fail(f"reviewed over cap for {repo}")
        if pending > target_pending:
            fail(f"pending over cap for {repo}")

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
        verify_snapshot_records(scope, snapshot)
        queue_payload = load_json(root / "REVIEW_QUEUE.json")
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
