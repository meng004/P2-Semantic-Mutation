#!/usr/bin/env python3
"""Verify supplemental R2 handoff SHA-256 bindings, counts, and SELF parent relationship."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_GATE = "SUPPLEMENTAL_ADMISSION_R2-r3"
PROHIBITED_VOCAB_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b|"
    r"(^|[^A-Za-z0-9_])(CE|OS|HP|TF|SI|fiber|stratum)([^A-Za-z0-9_]|$))"
)
DOWNSTREAM_SENTINEL_RE = re.compile(
    r"(?i)("
    r"\breadiness\b|"
    r"\bcanonical_freeze\b|"
    r"\bcanonical-freeze\b|"
    r"\bannotation\b|"
    r"\bprediction\b|"
    r"\bdetection_result\b|"
    r"\bdetection-result\b"
    r")"
)
FORBIDDEN_PATH_NAME_RE = re.compile(
    r"(?i)(^|/)(readiness|canonical_freeze|canonical-freeze|"
    r"annotation|prediction|detection)([._\-/]|$)"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_self_commit(handoff: dict[str, Any], *, cwd: Path) -> str | None:
    """Resolve handoff_commit.value SELF to current HEAD when present."""
    hc = handoff.get("handoff_commit") or {}
    value = hc.get("value")
    if value != "SELF":
        return value
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def verify_parent_relationship(
    handoff: dict[str, Any], *, cwd: Path, handoff_commit: str | None
) -> list[str]:
    errors: list[str] = []
    hc = handoff.get("handoff_commit") or {}
    required_parent = hc.get("direct_parent_required") or handoff.get("payload_commit")
    if not required_parent:
        errors.append("missing direct_parent_required / payload_commit")
        return errors
    if handoff.get("payload_commit") and handoff["payload_commit"] != required_parent:
        if handoff["payload_commit"] != required_parent:
            errors.append("payload_commit != direct_parent_required")
    if not handoff_commit:
        errors.append("unable to resolve handoff commit")
        return errors
    proc = subprocess.run(
        ["git", "rev-parse", f"{handoff_commit}^"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        errors.append(f"unable to resolve parent of {handoff_commit}")
        return errors
    actual_parent = proc.stdout.strip()
    if actual_parent != required_parent:
        errors.append(
            f"handoff parent mismatch: expected {required_parent}, got {actual_parent}"
        )
    return errors


def _resolve_declared_path(rel: str, *, handoff_path: Path, cwd: Path) -> Path | None:
    """Resolve a handoff-relative path against root, cwd, or repo root."""
    candidates = [
        handoff_path.parent / rel,
        cwd / rel,
        Path(__file__).resolve().parents[2] / rel,
    ]
    if rel.startswith("data/external_slice/supplemental_r2/"):
        suffix = rel.split("data/external_slice/supplemental_r2/", 1)[1]
        candidates.insert(0, handoff_path.parent / suffix)
    return next((p for p in candidates if p.is_file()), None)


def _earliest_review_stop(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> tuple[int, str]:
    if queue_count == 0:
        return 0, "queue_exhausted"
    pending = 0
    for index, decision in enumerate(decisions, start=1):
        if decision.get("decision") == "ADMIT_PENDING_REPRO":
            pending += 1
        hit_five = pending >= target_pending
        hit_cap = index >= max_reviewed
        hit_end = index >= queue_count
        if not (hit_five or hit_cap or hit_end):
            continue
        if hit_end:
            return index, "queue_exhausted"
        if hit_five:
            return index, "five_admit_pending_repro"
        return index, "twenty_reviewed"
    return -1, "invalid_early_stop"


def _review_stop_reason(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> str:
    _stop_at, reason = _earliest_review_stop(
        decisions,
        queue_count=queue_count,
        max_reviewed=max_reviewed,
        target_pending=target_pending,
    )
    return reason


def _command_log_sentinel_hits(command_log: dict[str, Any]) -> tuple[bool, bool]:
    readiness_hit = False
    freeze_hit = False
    for entry in command_log.get("entries") or []:
        blob = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        if not DOWNSTREAM_SENTINEL_RE.search(blob):
            continue
        lower = blob.lower()
        if re.search(r"\breadiness\b", lower):
            readiness_hit = True
        if re.search(r"\bcanonical[_-]freeze\b", lower) or re.search(
            r"\bcanonical\b.*\bfreeze\b", lower
        ):
            freeze_hit = True
        if re.search(r"\bannotation\b|\bprediction\b|\bdetection_result\b", lower):
            freeze_hit = True
    return readiness_hit, freeze_hit


def _forbidden_path_scan(root: Path) -> tuple[bool, bool, bool]:
    forbidden_path_hit = False
    readiness_file_hit = False
    freeze_file_hit = False
    if not root.is_dir():
        return False, False, False
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in {"VERIFICATION_LOG.json", "HANDOFF_SUPPLEMENTAL_R2.json", "SCOPE.json"}:
            continue
        if FORBIDDEN_PATH_NAME_RE.search(rel):
            forbidden_path_hit = True
            lower = rel.lower()
            if "readiness" in lower:
                readiness_file_hit = True
            if "canonical_freeze" in lower or "canonical-freeze" in lower:
                freeze_file_hit = True
            if any(
                token in lower
                for token in ("annotation", "prediction", "detection")
            ):
                freeze_file_hit = True
    return forbidden_path_hit, readiness_file_hit, freeze_file_hit


def _compute_confirmations(
    *,
    root: Path,
    scope: dict[str, Any],
    decisions: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, bool]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    a2_all_pending = all(
        d.get("crit_dual_arm_repro") == "PENDING" for d in decisions
    )
    analysis_id_all_blank = all(
        d.get("analysis_id") in (None, "") for d in decisions
    )
    vocab_clean = True
    for decision in decisions:
        for text_key in ("mechanism", "decision_reason"):
            if PROHIBITED_VOCAB_RE.search(decision.get(text_key) or ""):
                vocab_clean = False
                break
        if not vocab_clean:
            break
    command_log: dict[str, Any] = {}
    if (root / "COMMAND_LOG.json").is_file():
        command_log = load_json(root / "COMMAND_LOG.json")
    readiness_cmd, freeze_cmd = _command_log_sentinel_hits(command_log)
    path_hit, readiness_file, freeze_file = _forbidden_path_scan(root)
    existing_files_unchanged = True
    for rel, expected in (scope.get("input_sha256") or {}).items():
        path = repo_root / rel
        if not path.is_file() or sha256_file(path) != expected:
            existing_files_unchanged = False
            break
    return {
        "a2_all_pending": a2_all_pending,
        "analysis_id_all_blank": analysis_id_all_blank,
        "forbidden_data_absent": vocab_clean and not path_hit,
        "readiness_ran": bool(readiness_cmd or readiness_file),
        "canonical_freeze_claimed": bool(freeze_cmd or freeze_file),
        "existing_files_unchanged": existing_files_unchanged,
    }


def _project_quota_feasibility(
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


def recompute_admission_summary(
    *,
    root: Path,
    scope: dict[str, Any],
    quotas: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    sheet_rows: list[dict[str, str]],
    evidence_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Independently recompute handoff summary fields from artifacts."""
    if len(sheet_rows) != len(decisions):
        raise ValueError(
            f"sheet/decision cardinality mismatch {len(sheet_rows)} != {len(decisions)}"
        )
    manifest = evidence_snapshot.get("records") or []
    if len(manifest) != len(decisions):
        raise ValueError("evidence manifest cardinality mismatch")
    for decision, row, man in zip(decisions, sheet_rows, manifest):
        nid = decision["neutral_id"]
        if row.get("neutral_id") != nid or man.get("neutral_id") != nid:
            raise ValueError(f"sheet/evidence order mismatch around {nid}")
        if str(row.get("decision") or "") != str(decision.get("decision") or ""):
            raise ValueError(f"sheet/decision mismatch {nid}:decision")

    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    by_repo_q: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }
    for row in queue:
        by_repo_q.setdefault(row["repository"], []).append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }
    for decision in decisions:
        by_repo_d.setdefault(decision["repository"], []).append(decision)

    repository_review_counts: dict[str, Any] = {}
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        qrows = by_repo_q.get(repo, [])
        drows = by_repo_d.get(repo, [])
        admits = sum(1 for d in drows if d.get("decision") == "ADMIT_PENDING_REPRO")
        excluded = sum(1 for d in drows if d.get("decision") == "EXCLUDED")
        excl_classes: dict[str, int] = {}
        for d in drows:
            if d.get("decision") != "EXCLUDED":
                continue
            key = d.get("exclusion_class") or "(A1/A3 fail)"
            excl_classes[key] = excl_classes.get(key, 0) + 1
        status_counts: dict[str, int] = {}
        for row in qrows:
            st = str(row.get("review_status") or "")
            status_counts[st] = status_counts.get(st, 0) + 1
        reason = _review_stop_reason(
            drows,
            queue_count=len(qrows),
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        repository_review_counts[repo] = {
            "queue_size": len(qrows),
            "reviewed": len(drows),
            "admit_pending_repro": admits,
            "excluded": excluded,
            "exclusion_class_counts": excl_classes,
            "review_status_counts": status_counts,
            "stop_reason": reason,
        }

    feasibility = _project_quota_feasibility(quotas, decisions)
    return {
        "decision_totals": {
            "decisions": len(decisions),
            "admit_pending_repro": sum(
                1 for d in decisions if d.get("decision") == "ADMIT_PENDING_REPRO"
            ),
            "excluded": sum(1 for d in decisions if d.get("decision") == "EXCLUDED"),
        },
        "repository_review_counts": repository_review_counts,
        "quota_feasibility": feasibility,
        "confirmations": _compute_confirmations(
            root=root, scope=scope, decisions=decisions
        ),
    }


def _deep_equal(expected: Any, actual: Any, *, path: str) -> list[str]:
    errors: list[str] = []
    if type(expected) is not type(actual) and not (
        isinstance(expected, (int, float)) and isinstance(actual, (int, float))
    ):
        # Allow dict key order differences only via recursive compare.
        if not (isinstance(expected, dict) and isinstance(actual, dict)):
            if expected != actual:
                errors.append(f"{path}: expected {expected!r}, got {actual!r}")
            return errors
    if isinstance(expected, dict):
        exp_keys = set(expected)
        act_keys = set(actual)
        for key in sorted(exp_keys - act_keys):
            errors.append(f"{path}.{key}: missing in handoff")
        for key in sorted(act_keys - exp_keys):
            errors.append(f"{path}.{key}: unexpected in handoff")
        for key in sorted(exp_keys & act_keys):
            errors.extend(
                _deep_equal(expected[key], actual[key], path=f"{path}.{key}")
            )
        return errors
    if isinstance(expected, list):
        if len(expected) != len(actual):
            errors.append(
                f"{path}: list length expected {len(expected)}, got {len(actual)}"
            )
            return errors
        for idx, (exp_item, act_item) in enumerate(zip(expected, actual)):
            errors.extend(_deep_equal(exp_item, act_item, path=f"{path}[{idx}]"))
        return errors
    if expected != actual:
        errors.append(f"{path}: expected {expected!r}, got {actual!r}")
    return errors


def verify_handoff_summary_counts(
    handoff: dict[str, Any], *, handoff_path: Path
) -> list[str]:
    """Recompute totals/stop/pending/shortfalls from artifacts and compare strictly."""
    root = handoff_path.parent
    required = [
        "SCOPE.json",
        "QUOTAS.json",
        "REVIEW_QUEUE.json",
        "REVIEW_DECISIONS.json",
        "admission_sheet.cursor_candidate.csv",
        "EVIDENCE_SNAPSHOT.json",
    ]
    has_artifacts = all((root / name).is_file() for name in required)
    has_claims = any(
        key in handoff
        for key in (
            "decision_totals",
            "repository_review_counts",
            "quota_feasibility",
            "confirmations",
        )
    )
    if not has_artifacts:
        if has_claims:
            return ["summary claims present but admission artifacts missing"]
        # Hash/parent-only fixtures may omit the admission artifact set.
        return []
    errors: list[str] = []
    if not has_claims:
        return [
            "missing decision_totals / repository_review_counts / "
            "quota_feasibility / confirmations"
        ]

    scope = load_json(root / "SCOPE.json")
    quotas = load_json(root / "QUOTAS.json")
    queue = load_json(root / "REVIEW_QUEUE.json")["records"]
    decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
    with (root / "admission_sheet.cursor_candidate.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        sheet_rows = list(csv.DictReader(handle))
    evidence_snapshot = load_json(root / "EVIDENCE_SNAPSHOT.json")
    try:
        expected = recompute_admission_summary(
            root=root,
            scope=scope,
            quotas=quotas,
            queue=queue,
            decisions=decisions,
            sheet_rows=sheet_rows,
            evidence_snapshot=evidence_snapshot,
        )
    except ValueError as exc:
        return [f"summary recompute failed: {exc}"]

    errors.extend(
        _deep_equal(
            expected["decision_totals"],
            handoff.get("decision_totals"),
            path="decision_totals",
        )
    )
    errors.extend(
        _deep_equal(
            expected["repository_review_counts"],
            handoff.get("repository_review_counts"),
            path="repository_review_counts",
        )
    )
    errors.extend(
        _deep_equal(
            expected["quota_feasibility"],
            handoff.get("quota_feasibility"),
            path="quota_feasibility",
        )
    )
    errors.extend(
        _deep_equal(
            expected["confirmations"],
            handoff.get("confirmations"),
            path="confirmations",
        )
    )
    return errors


def verify_gate_binding(handoff: dict[str, Any], *, handoff_path: Path) -> list[str]:
    # Hash/parent-only fixtures may use alternate filenames without gate claims.
    if handoff_path.name != "HANDOFF_SUPPLEMENTAL_R2.json":
        return []
    errors: list[str] = []
    gate = handoff.get("gate_requested")
    if gate != EXPECTED_GATE:
        errors.append(f"handoff gate_requested {gate!r} != {EXPECTED_GATE!r}")
    vlog_path = handoff_path.parent / "VERIFICATION_LOG.json"
    if vlog_path.is_file():
        vlog = load_json(vlog_path)
        vgate = vlog.get("gate_requested")
        if vgate != EXPECTED_GATE:
            errors.append(
                f"verification_log gate_requested {vgate!r} != {EXPECTED_GATE!r}"
            )
        if gate != vgate:
            errors.append(
                f"gate mismatch between handoff and verification_log: "
                f"{gate!r} vs {vgate!r}"
            )
    return errors


def verify_handoff_hashes(
    handoff_path: Path,
    *,
    cwd: Path | None = None,
    check_parent: bool = True,
    git_cwd: Path | None = None,
) -> int:
    cwd = cwd or Path.cwd()
    git_cwd = git_cwd or cwd
    handoff = load_json(handoff_path)
    mismatches: list[str] = []
    mismatches.extend(verify_gate_binding(handoff, handoff_path=handoff_path))

    for rel, expected in (handoff.get("file_sha256") or {}).items():
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing file {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    for rel, expected in (handoff.get("evidence_sha256") or {}).items():
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing evidence {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    mismatches.extend(verify_handoff_summary_counts(handoff, handoff_path=handoff_path))

    # SELF resolution always attempted for reporting.
    resolved = resolve_self_commit(handoff, cwd=git_cwd)
    if (handoff.get("handoff_commit") or {}).get("value") == "SELF" and not resolved:
        mismatches.append("SELF resolution failed")

    if check_parent and (handoff.get("handoff_commit") or {}).get(
        "direct_parent_required"
    ):
        mismatches.extend(
            verify_parent_relationship(
                handoff, cwd=git_cwd, handoff_commit=resolved
            )
        )

    if mismatches:
        print("HASH_CHECK_FAIL", file=sys.stderr)
        for item in mismatches:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print("HASH_CHECK_OK")
    print(f"handoff_commit_resolved={resolved}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument(
        "--skip-parent-check",
        action="store_true",
        help="Skip git parent relationship check (fixture use)",
    )
    args = parser.parse_args(argv)
    return verify_handoff_hashes(
        args.handoff, check_parent=not args.skip_parent_check
    )


if __name__ == "__main__":
    raise SystemExit(main())
