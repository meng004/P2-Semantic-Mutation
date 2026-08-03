"""Binding/admission negatives for supplemental mining R2 (§6.2–6.5)."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "data" / "external_slice" / "supplemental_r2"
MINER_PATH = ROOT / "scripts" / "external_slice" / "mine_supplemental_r2.py"
CHECKER_PATH = ROOT / "scripts" / "external_slice" / "check_supplemental_r2_admission.py"
HANDOFF_PATH = ROOT / "scripts" / "external_slice" / "check_supplemental_r2_handoff_hashes.py"

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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


miner = load_module(MINER_PATH, "mine_supplemental_r2")
checker = load_module(CHECKER_PATH, "check_supplemental_r2_admission")
handoff_mod = load_module(HANDOFF_PATH, "check_supplemental_r2_handoff_hashes")


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


def make_issue(**kwargs: Any) -> dict[str, Any]:
    # Reuse miner test helpers via local minimal copy.
    number = kwargs["number"]
    owner = kwargs["owner"]
    name = kwargs["name"]
    return {
        "__typename": kwargs.get("typename", "Issue"),
        "id": f"ISSUE_{owner}_{name}_{number}",
        "number": number,
        "url": kwargs.get("url")
        or f"https://github.com/{owner}/{name}/issues/{number}",
        "state": kwargs.get("state", "CLOSED"),
        "title": kwargs["title"],
        "bodyText": kwargs.get("body", ""),
        "createdAt": kwargs["created_at"],
        "updatedAt": kwargs.get("updated_at", kwargs["created_at"]),
        "closedAt": kwargs.get("closed_at", "2026-01-02T00:00:00Z"),
        "labels": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"name": lab} for lab in kwargs.get("labels", [])],
        },
    }


def make_page(owner: str, name: str, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "data": {
            "repository": {
                "issues": {
                    "totalCount": len(nodes),
                    "pageInfo": {"hasNextPage": False, "endCursor": "E"},
                    "nodes": nodes,
                }
            }
        }
    }


def build_fixture_runner() -> Any:
    scope = json.loads((FROZEN / "SCOPE.json").read_text())
    pages: dict[tuple[str, str], dict[str, Any]] = {}
    for repo in scope["repositories"]:
        # Enough issues to exercise stop-rule / exclusions.
        nodes = []
        for i, n in enumerate([30, 29, 28, 27, 26], start=0):
            title = "wrong result" if i < 4 else "docs only"
            month = 6 - i
            nodes.append(
                make_issue(
                    number=n,
                    owner=repo["owner"],
                    name=repo["name"],
                    created_at=f"2025-0{month}-01T00:00:00Z",
                    title=title,
                    body="numerical regression" if i == 1 else "",
                )
            )
        pages[(repo["owner"], repo["name"])] = make_page(
            repo["owner"], repo["name"], nodes
        )

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        key = (variables["owner"], variables["name"])
        return 0, json.dumps(pages[key]), ""

    return runner


def write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SHEET_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def build_decision_from_queue_row(
    row: dict[str, Any],
    *,
    admit: bool = True,
    exclusion_class: str = "",
) -> dict[str, Any]:
    sha_a = "a" * 40
    sha_b = "b" * 40
    if admit:
        return {
            "neutral_id": row["neutral_id"],
            "snapshot_record_id": row["snapshot_record_id"],
            "snapshot_record_sha256": row["snapshot_record_sha256"],
            "repository": row["repository"],
            "issue_node_id": row["issue_node_id"],
            "issue_number": row["issue_number"],
            "issue_url": row["issue_url"],
            "repository_review_order": row["repository_review_order"],
            "matched_phrases": list(row["matched_phrases"]),
            "buggy_sha": sha_a,
            "fixed_sha": sha_b,
            "public_issue_url": row["issue_url"],
            "public_fix_url": f"{row['issue_url'].replace('/issues/', '/commit/')}-fix",
            "mechanism": "restores the numerical return value for the reported input.",
            "exclusion_class": "",
            "crit_real_public_fix": "PASS",
            "crit_in_numerical_scope": "PASS",
            "crit_dual_arm_repro": "PENDING",
            "decision": "ADMIT_PENDING_REPRO",
            "decision_reason": "A1 and A3 pass on public evidence.",
            "analysis_id": "",
        }
    return {
        "neutral_id": row["neutral_id"],
        "snapshot_record_id": row["snapshot_record_id"],
        "snapshot_record_sha256": row["snapshot_record_sha256"],
        "repository": row["repository"],
        "issue_node_id": row["issue_node_id"],
        "issue_number": row["issue_number"],
        "issue_url": row["issue_url"],
        "repository_review_order": row["repository_review_order"],
        "matched_phrases": list(row["matched_phrases"]),
        "buggy_sha": "",
        "fixed_sha": "",
        "public_issue_url": row["issue_url"],
        "public_fix_url": "",
        "mechanism": "excluded as documentation-only report.",
        "exclusion_class": exclusion_class or "documentation",
        "crit_real_public_fix": "FAIL",
        "crit_in_numerical_scope": "FAIL",
        "crit_dual_arm_repro": "PENDING",
        "decision": "EXCLUDED",
        "decision_reason": "documentation exclusion class applies.",
        "analysis_id": "",
    }


def build_valid_payload(root: Path, *, admits_per_quota_repo: int = 3) -> None:
    assert miner.cmd_retrieve(root, runner=build_fixture_runner()) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())["records"]
    quotas = json.loads((root / "QUOTAS.json").read_text())
    positive = {
        e["repo"]
        for e in quotas["readiness_quota_order"]
        if int(e["additional_ready_target"]) > 0
    }
    decisions: list[dict[str, Any]] = []
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo.setdefault(row["repository"], []).append(row)
    for repo, rows in by_repo.items():
        admit_n = admits_per_quota_repo if repo in positive else 1
        for idx, row in enumerate(rows):
            if idx < admit_n:
                decisions.append(build_decision_from_queue_row(row, admit=True))
            elif idx == admit_n:
                decisions.append(build_decision_from_queue_row(row, admit=False))
            else:
                break
    _write_json(
        root / "REVIEW_DECISIONS.json",
        {"schema_version": 1, "task": "SUPPLEMENTAL_MINING_R2", "decisions": decisions},
    )
    assert miner.cmd_build_payload(root) == 0


CANDIDATE_ARTIFACTS = (
    "ISSUE_SNAPSHOT.json",
    "REVIEW_QUEUE.json",
    "REVIEW_DECISIONS.json",
    "admission_sheet.cursor_candidate.csv",
    "EVIDENCE_SNAPSHOT.json",
    "HANDOFF_SUPPLEMENTAL_R2.json",
    "transport_pages",
    "admission_evidence",
)


def present_candidates(root: Path) -> set[str]:
    return {name for name in CANDIDATE_ARTIFACTS if (root / name).exists()}


def assert_checker_fails_without_new_mint(root: Path, before: set[str]) -> None:
    code = checker.verify_admission(root)
    assert code != 0
    after = present_candidates(root)
    assert after <= before, f"newly minted candidates: {after - before}"


def test_positive_admission_check(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=3)
    assert checker.verify_admission(root) == 0


@pytest.mark.parametrize(
    "target,field",
    [
        ("log_top", "run_id"),
        ("log_top", "code_commit"),
        ("log_entry", "run_id"),
        ("log_entry", "code_commit"),
        ("snapshot", "run_id"),
        ("snapshot", "code_commit"),
        ("queue", "run_id"),
        ("queue", "code_commit"),
    ],
)
def test_run_code_binding_field_tamper(
    tmp_path: Path, target: str, field: str
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    if target == "log_top":
        payload = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "COMMAND_LOG.json", payload)
    elif target == "log_entry":
        payload = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
        payload["entries"][0][field] = (
            "0" * 40 if field == "code_commit" else "tampered-run"
        )
        _write_json(root / "COMMAND_LOG.json", payload)
    elif target == "snapshot":
        payload = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "ISSUE_SNAPSHOT.json", payload)
    else:
        payload = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "REVIEW_QUEUE.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_queue_rebuild_preserves_run_code_binding(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    (root / "REVIEW_QUEUE.json").unlink()
    assert miner.cmd_build_queue(root) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    assert queue["run_id"] == snapshot["run_id"]
    assert queue["code_commit"] == snapshot["code_commit"]
    assert checker.verify_admission(root) == 0


def test_diagnostic_run_code_mismatch_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    _write_json(
        root / "RETRIEVAL_HARD_FAIL.json",
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "invariant": "unexpected_error",
            "detail": "stale",
            "timestamp_utc": "2026-08-02T14:14:29Z",
            "run_id": "other-run",
            "code_commit": snap["code_commit"],
            "terminal": True,
        },
    )
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
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
    ],
)
def test_queue_copied_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    row = queue["records"][0]
    if field == "issue_number":
        row[field] = int(row[field]) + 99
    elif field == "matched_phrases":
        row[field] = ["tampered phrase"]
    elif field == "repository_order":
        row[field] = 99
    else:
        row[field] = f"TAMPERED-{row.get(field)}"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_snapshot_record_hash_mutation(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"][0]["snapshot_record_sha256"] = "0" * 64
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_false_phrase_match(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"][0]["matched_phrases"] = ["not a frozen phrase"]
    # Keep hash consistent with mutated body so hash check isn't the only failure.
    body = {
        k: snap["records"][0][k]
        for k in snap["records"][0]
        if k != "snapshot_record_sha256"
    }
    snap["records"][0]["snapshot_record_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_wrong_phrase_order(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    # Find a record with >=2 phrases if possible; else inject reversed pair.
    rec = snap["records"][0]
    rec["matched_phrases"] = list(reversed(rec["matched_phrases"])) or [
        "incorrect value",
        "wrong result",
    ]
    if len(rec["matched_phrases"]) == 1:
        rec["matched_phrases"] = ["incorrect value", "wrong result"]
        rec["match_surfaces"] = {
            "incorrect value": ["title"],
            "wrong result": ["title"],
        }
    body = {k: rec[k] for k in rec if k != "snapshot_record_sha256"}
    rec["snapshot_record_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_reordered_union(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    pymc = [r for r in queue["records"] if r["repository"] == "pymc-devs/pymc"]
    if len(pymc) >= 2:
        # Swap first two pymc rows in the full list.
        i0 = queue["records"].index(pymc[0])
        i1 = queue["records"].index(pymc[1])
        queue["records"][i0], queue["records"][i1] = (
            queue["records"][i1],
            queue["records"][i0],
        )
        _write_json(root / "REVIEW_QUEUE.json", queue)
        assert_checker_fails_without_new_mint(root, before)
    else:
        pytest.skip("need >=2 pymc rows")


def test_wrong_neutral_id(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    queue["records"][0]["neutral_id"] = "EXT-pymc-99"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_snapshot_item(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"].pop(0)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_extra_queue_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    clone = dict(queue["records"][0])
    clone["neutral_id"] = "EXT-pymc-99"
    clone["union_order"] = 99
    clone["repository_review_order"] = 99
    queue["records"].append(clone)
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
        "neutral_id",
        "snapshot_record_id",
        "snapshot_record_sha256",
        "repository",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "repository_review_order",
        "matched_phrases",
    ],
)
def test_decision_copied_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    d = payload["decisions"][0]
    if field == "issue_number":
        d[field] = int(d[field]) + 7
    elif field == "matched_phrases":
        d[field] = ["tampered"]
    elif field == "repository_review_order":
        d[field] = 99
    else:
        d[field] = f"TAMPERED-{d.get(field)}"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_decision_for_unreviewed_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    # Mark first as NOT_REVIEWED_AFTER_STOP while decision remains.
    queue["records"][0]["review_status"] = "NOT_REVIEWED_AFTER_STOP"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_invalid_exclusion_class(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    for d in payload["decisions"]:
        if d["decision"] == "EXCLUDED":
            d["exclusion_class"] = "not-a-real-class"
            break
    else:
        payload["decisions"][0]["decision"] = "EXCLUDED"
        payload["decisions"][0]["exclusion_class"] = "not-a-real-class"
        payload["decisions"][0]["crit_real_public_fix"] = "FAIL"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_short_sha_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["buggy_sha"] = "abc"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_public_url(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["public_fix_url"] = ""
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_non_pending_a2(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_dual_arm_repro"] = "PASS"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_admit_inconsistency(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_in_numerical_scope"] = "FAIL"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_reordered_decisions(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    if len(payload["decisions"]) < 2:
        pytest.skip("need >=2 decisions")
    payload["decisions"][0], payload["decisions"][1] = (
        payload["decisions"][1],
        payload["decisions"][0],
    )
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
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
    ],
)
def test_sheet_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    if field == "crit_dual_arm_repro":
        rows[0][field] = "PASS"
    elif field == "source_cohort":
        rows[0][field] = "tampered"
    else:
        rows[0][field] = f"TAMPERED-{rows[0].get(field)}"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_wrong_cohort(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["source_cohort"] = "supplemental_r1"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_nonblank_alias(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["analysis_id"] = "CE-01"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_forbidden_vocabulary_in_sheet(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["mechanism"] = "uses operator fiber mapping"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
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
    ],
)
def test_evidence_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    nid = manifest["records"][0]["neutral_id"]
    path = root / "admission_evidence" / nid / "evidence.json"
    evidence = json.loads(path.read_text())
    if field == "issue_number":
        evidence[field] = int(evidence[field]) + 3
    elif field == "crit_dual_arm_repro":
        evidence[field] = "PASS"
    else:
        evidence[field] = f"TAMPERED-{evidence.get(field)}"
    _write_json(path, evidence)
    # Keep manifest hash pointing at old bytes → hash mismatch also fails.
    assert_checker_fails_without_new_mint(root, before)


def test_evidence_hash_mismatch(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    manifest["records"][0]["sha256"] = "0" * 64
    _write_json(root / "EVIDENCE_SNAPSHOT.json", manifest)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_evidence_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    nid = manifest["records"][0]["neutral_id"]
    shutil.rmtree(root / "admission_evidence" / nid)
    manifest["records"].pop(0)
    _write_json(root / "EVIDENCE_SNAPSHOT.json", manifest)
    assert_checker_fails_without_new_mint(root, before)


def test_extra_sheet_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    clone = dict(rows[0])
    clone["neutral_id"] = "EXT-pymc-99"
    rows.append(clone)
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_changed_starting_counts(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["starting_state"]["accepted_ready_defects"] = 17
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_quota_target_change(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["readiness_quota_order"][0]["additional_ready_target"] = 9
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_replacement_repository(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["readiness_quota_order"][0]["repo"] = "numpy/numpy"
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_incorrect_projection(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["projection_if_quotas_met"]["qualifying_projects"] = 4
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_claims_ready_success(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="a" * 40) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["claims_ready_success"] = True
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_missing_shortfall_disclosure(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    # Only 1 admit per positive repo → shortfall expected.
    build_valid_payload(root, admits_per_quota_repo=1)
    assert miner.cmd_write_handoff(root, payload_commit="b" * 40) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["shortfalls"] = []
    handoff["quota_feasibility"]["status"] = "DISTRIBUTION_TARGET_AT_RISK"
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_hash_mismatch(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="c" * 40) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["file_sha256"]["ISSUE_SNAPSHOT.json"] = "0" * 64
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=False, git_cwd=ROOT
    )
    assert code != 0


def test_handoff_self_resolution_and_parent(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    parent = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    handoff = {
        "file_sha256": {
            "SCOPE.json": hashlib.sha256((root / "SCOPE.json").read_bytes()).hexdigest()
        },
        "evidence_sha256": {},
        "payload_commit": parent,
        "handoff_commit": {
            "value": "SELF",
            "direct_parent_required": parent,
            "resolution": "git rev-parse HEAD",
        },
    }
    path = root / "HANDOFF_SELF.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=True, git_cwd=ROOT
    )
    assert code == 0

    handoff["handoff_commit"]["direct_parent_required"] = "0" * 40
    handoff["payload_commit"] = "0" * 40
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=True, git_cwd=ROOT
    )
    assert code != 0
    assert head


def test_stale_code_hash_in_handoff(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="d" * 40) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    script_key = "scripts/external_slice/mine_supplemental_r2.py"
    handoff["file_sha256"][script_key] = "1" * 64
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=False, git_cwd=ROOT
    )
    assert code != 0


def test_validate_decisions_cli(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_validate_decisions(root) == 0
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_dual_arm_repro"] = "PASS"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert miner.cmd_validate_decisions(root) != 0
