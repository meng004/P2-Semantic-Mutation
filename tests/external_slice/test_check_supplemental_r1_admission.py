"""TDD tests for supplemental mining R1 admission checker (R1-r2 queue binding)."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "external_slice" / "check_supplemental_r1_admission.py"
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
FULL_A = "a" * 40
FULL_B = "b" * 40


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R1",
        "baseline_commit": "0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a",
        "created_cutoff": "2026-08-01",
        "search_sort": "created",
        "search_order": "desc",
        "max_results_per_phrase": 20,
        "max_reviewed_per_repo": 20,
        "target_pending_per_repo": 5,
        "repositories": [
            {
                "repo": "pymc-devs/pymc",
                "id_prefix": "EXT-pymc-",
                "restriction": "numerical kernels only",
            }
        ],
        "phrases": ["wrong result"],
        "input_sha256": {},
        "forbidden_actions": ["A2 build or trigger execution"],
    }


def _row(
    *,
    neutral_id: str = "EXT-pymc-01",
    repo: str = "pymc-devs/pymc",
    issue: int = 1,
    decision: str = "ADMIT_PENDING_REPRO",
    a1: str = "PASS",
    a2: str = "PENDING",
    a3: str = "PASS",
    buggy: str = FULL_A,
    fixed: str = FULL_B,
    exclusion: str = "",
    analysis_id: str = "",
    mechanism: str = "restores the returned density normalisation constant.",
) -> dict[str, str]:
    return {
        "neutral_id": neutral_id,
        "repo": repo.split("/")[-1],
        "issue_url": f"https://github.com/{repo}/issues/{issue}",
        "buggy_sha": buggy,
        "fixed_sha": fixed,
        "mechanism_sentence": mechanism,
        "crit_real_defect": a1,
        "crit_dual_arm_repro": a2,
        "crit_in_scope": a3,
        "decision": decision,
        "exclusion_reason": exclusion,
        "analysis_id": analysis_id,
    }


def _decision_from_row(row: dict[str, str], order: int = 1, repo: str = "pymc-devs/pymc") -> dict[str, Any]:
    return {
        "neutral_id": row["neutral_id"],
        "repo": repo,
        "issue_number": int(row["issue_url"].rsplit("/", 1)[-1]),
        "issue_url": row["issue_url"],
        "fix_url": f"https://github.com/{repo}/commit/{row['fixed_sha']}"
        if row["fixed_sha"]
        else "",
        "buggy_sha": row["buggy_sha"],
        "fixed_sha": row["fixed_sha"],
        "mechanism_sentence": row["mechanism_sentence"],
        "crit_real_defect": row["crit_real_defect"],
        "crit_dual_arm_repro": row["crit_dual_arm_repro"],
        "crit_in_scope": row["crit_in_scope"],
        "decision": row["decision"],
        "exclusion_reason": row["exclusion_reason"],
        "analysis_id": row["analysis_id"],
        "rationales": {
            "real_defect": "A public defect report and an identifiable public fix commit are linked.",
            "dual_arm_repro": "No same-trigger dual-arm result is claimed in this task.",
            "in_scope": "The changed callable maps float-vector input to a float numerical output.",
        },
        "evidence_urls": [
            row["issue_url"],
            f"https://github.com/{repo}/commit/{row['fixed_sha']}"
            if row["fixed_sha"]
            else row["issue_url"],
        ],
        "review_order": order,
        "review_status": "REVIEWED",
    }


def _write_evidence(
    root: Path,
    row: dict[str, str],
    *,
    scope_sha: str,
    search_sha: str,
    decisions_sha: str,
) -> None:
    case_dir = root / row["neutral_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "neutral_id": row["neutral_id"],
        "source_pool": "supplemental_mining_r1",
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "review_decisions_sha256": decisions_sha,
        "issue_url": row["issue_url"],
        "fix_url": f"https://github.com/pymc-devs/pymc/commit/{row['fixed_sha']}"
        if row["fixed_sha"]
        else "",
        "buggy_sha": row["buggy_sha"],
        "fixed_sha": row["fixed_sha"],
        "criteria": {
            "real_defect": row["crit_real_defect"],
            "dual_arm_repro": row["crit_dual_arm_repro"],
            "in_scope": row["crit_in_scope"],
        },
        "rationales": {
            "real_defect": "A public defect report and an identifiable public fix commit are linked.",
            "dual_arm_repro": "No same-trigger dual-arm result is claimed in this task.",
            "in_scope": "The changed callable maps float-vector input to a float numerical output.",
        },
        "evidence_urls": [row["issue_url"]],
        "mechanism_sentence": row["mechanism_sentence"],
    }
    (case_dir / "evidence.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _valid_fixture(tmp_path: Path) -> dict[str, Path]:
    base = tmp_path / "data" / "external_slice" / "supplemental_r1"
    scope_path = base / "SCOPE.json"
    snapshot_path = base / "SEARCH_SNAPSHOT.json"
    queue_path = base / "REVIEW_QUEUE.json"
    decisions_path = base / "REVIEW_DECISIONS.json"
    sheet_path = base / "admission_sheet.cursor_candidate.csv"
    evidence_root = base / "admission_evidence"
    existing = tmp_path / "existing.csv"
    pilot = tmp_path / "pilot.csv"

    protocol = tmp_path / "research" / "prereg_v2" / "external_slice_protocol.md"
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_bytes(b"protocol-fixture\n")
    scope = _scope()
    scope["input_sha256"] = {
        str(protocol.relative_to(tmp_path)): _sha256_file(protocol),
    }
    _write_json(scope_path, scope)
    scope_sha = _sha256_file(scope_path)
    q = 'repo:pymc-devs/pymc is:issue is:closed created:<=2026-08-01 "wrong result"'
    row = _row()
    snapshot = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "queries": [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "q": q,
                "total_count": 1,
                "incomplete_results": False,
                "returned": 1,
                "issue_count": 1,
                "pull_count": 0,
                "items": [
                    {
                        "repo": "pymc-devs/pymc",
                        "phrase": "wrong result",
                        "issue_number": 1,
                        "issue_url": row["issue_url"],
                        "state": "closed",
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
            }
        ],
    }
    _write_json(snapshot_path, snapshot)
    search_sha = _sha256_file(snapshot_path)
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": [
            {
                "neutral_id": "EXT-pymc-01",
                "repo": "pymc-devs/pymc",
                "issue_number": 1,
                "issue_url": row["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
                "phrases": ["wrong result"],
                "review_status": "PENDING_REVIEW",
            }
        ],
    }
    _write_json(queue_path, queue)
    decisions = {"schema_version": 1, "decisions": [_decision_from_row(row)]}
    _write_json(decisions_path, decisions)
    _write_sheet(sheet_path, [row])
    decisions_sha = _sha256_file(decisions_path)
    _write_evidence(
        evidence_root,
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
    )
    _write_sheet(existing, [_row(neutral_id="EXT-fftw-01", repo="FFTW/fftw3", issue=20)])
    _write_sheet(pilot, [_row(neutral_id="EXT-numpy-01", repo="numpy/numpy", issue=1)])
    return {
        "scope": scope_path,
        "snapshot": snapshot_path,
        "queue": queue_path,
        "decisions": decisions_path,
        "sheet": sheet_path,
        "evidence_root": evidence_root,
        "existing": existing,
        "pilot": pilot,
        "fixture_root": tmp_path,
    }


def _run(paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--scope",
            str(paths["scope"]),
            "--snapshot",
            str(paths["snapshot"]),
            "--queue",
            str(paths["queue"]),
            "--decisions",
            str(paths["decisions"]),
            "--sheet",
            str(paths["sheet"]),
            "--evidence-root",
            str(paths["evidence_root"]),
            "--existing-sheet",
            str(paths["existing"]),
            "--pilot-sheet",
            str(paths["pilot"]),
            "--fixture-root",
            str(paths["fixture_root"]),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_accepts_valid_pending_row(tmp_path: Path) -> None:
    result = _run(_valid_fixture(tmp_path))
    assert result.returncode == 0, result.stderr


def test_rejects_repo_outside_scope(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row = _row(repo="numpy/numpy", issue=99)
    _write_sheet(paths["sheet"], [row])
    decisions = {"schema_version": 1, "decisions": [_decision_from_row(row, repo="numpy/numpy")]}
    _write_json(paths["decisions"], decisions)
    result = _run(paths)
    assert result.returncode != 0


def test_rejects_decision_queue_url_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["issue_url"] = "https://github.com/pymc-devs/pymc/issues/999"
    _write_json(paths["decisions"], payload)
    # Keep sheet matching old URL so sheet/decision set still 1:1 by id, but URL mismatches queue.
    result = _run(paths)
    assert result.returncode != 0
    assert "issue_url mismatch" in result.stderr


def test_rejects_decision_queue_repo_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["repo"] = "jax-ml/jax"
    _write_json(paths["decisions"], payload)
    result = _run(paths)
    assert result.returncode != 0
    assert (
        "repository mismatch" in result.stderr
        or "outside SCOPE" in result.stderr
        or "queue-head" in result.stderr
    )


def test_rejects_decision_issue_number_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["issue_number"] = 999
    _write_json(paths["decisions"], payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "issue_number mismatch" in result.stderr


def test_rejects_swapped_review_order(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    # Add a second queue head and swapped decisions.
    row1 = _row(neutral_id="EXT-pymc-01", issue=1)
    row2 = _row(neutral_id="EXT-pymc-02", issue=2, buggy="c" * 40, fixed="d" * 40)
    scope_sha = _sha256_file(paths["scope"])
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": _sha256_file(paths["snapshot"]),
        "records": [
            {
                "neutral_id": "EXT-pymc-01",
                "repo": "pymc-devs/pymc",
                "issue_number": 1,
                "issue_url": row1["issue_url"],
                "state": "closed",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "neutral_id": "EXT-pymc-02",
                "repo": "pymc-devs/pymc",
                "issue_number": 2,
                "issue_url": row2["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ],
    }
    _write_json(paths["queue"], queue)
    # Intentionally assign review_order swapped relative to queue head order.
    decisions = {
        "schema_version": 1,
        "decisions": [
            _decision_from_row(row2, order=1),
            _decision_from_row(row1, order=2),
        ],
    }
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], [row2, row1])
    decisions_sha = _sha256_file(paths["decisions"])
    search_sha = _sha256_file(paths["snapshot"])
    for row in (row1, row2):
        _write_evidence(
            paths["evidence_root"],
            row,
            scope_sha=scope_sha,
            search_sha=search_sha,
            decisions_sha=decisions_sha,
        )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr or "review_order" in result.stderr


def test_rejects_skipped_queue_head(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row1 = _row(neutral_id="EXT-pymc-01", issue=1)
    row2 = _row(neutral_id="EXT-pymc-02", issue=2, buggy="c" * 40, fixed="d" * 40)
    scope_sha = _sha256_file(paths["scope"])
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": _sha256_file(paths["snapshot"]),
        "records": [
            {
                "neutral_id": "EXT-pymc-01",
                "repo": "pymc-devs/pymc",
                "issue_number": 1,
                "issue_url": row1["issue_url"],
                "state": "closed",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "neutral_id": "EXT-pymc-02",
                "repo": "pymc-devs/pymc",
                "issue_number": 2,
                "issue_url": row2["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ],
    }
    _write_json(paths["queue"], queue)
    # Skip queue head 01; only decide 02.
    decisions = {"schema_version": 1, "decisions": [_decision_from_row(row2, order=1)]}
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], [row2])
    decisions_sha = _sha256_file(paths["decisions"])
    _write_evidence(
        paths["evidence_root"],
        row2,
        scope_sha=scope_sha,
        search_sha=_sha256_file(paths["snapshot"]),
        decisions_sha=decisions_sha,
    )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr


def test_rejects_decisions_beyond_stop_boundary(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = [
        _row(
            neutral_id=f"EXT-pymc-{i:02d}",
            issue=i,
            buggy=f"{i:040d}",
            fixed=f"{i + 100:040d}",
        )
        for i in range(1, 7)
    ]
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope["target_pending_per_repo"] = 2
    _write_json(paths["scope"], scope)
    scope_sha = _sha256_file(paths["scope"])
    # Rewrite snapshot scope hash.
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["scope_sha256"] = scope_sha
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": [
            {
                "neutral_id": row["neutral_id"],
                "repo": "pymc-devs/pymc",
                "issue_number": int(row["issue_url"].rsplit("/", 1)[-1]),
                "issue_url": row["issue_url"],
                "state": "closed",
                "created_at": f"2026-01-{i:02d}T00:00:00Z",
            }
            for i, row in enumerate(rows, start=1)
        ],
    }
    _write_json(paths["queue"], queue)
    # 3 pending admits exceeds stop after 2 pending.
    decisions = {
        "schema_version": 1,
        "decisions": [_decision_from_row(row, order=i) for i, row in enumerate(rows[:3], 1)],
    }
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], rows[:3])
    decisions_sha = _sha256_file(paths["decisions"])
    for row in rows[:3]:
        _write_evidence(
            paths["evidence_root"],
            row,
            scope_sha=scope_sha,
            search_sha=search_sha,
            decisions_sha=decisions_sha,
        )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr or "pending" in result.stderr.lower()


def test_rejects_a2_not_pending(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row = _row(a2="PASS")
    _write_sheet(paths["sheet"], [row])
    decisions = {"schema_version": 1, "decisions": [_decision_from_row(row)]}
    _write_json(paths["decisions"], decisions)
    result = _run(paths)
    assert result.returncode != 0
    assert "PENDING" in result.stderr


def test_rejects_missing_evidence_record(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    (paths["evidence_root"] / "EXT-pymc-01" / "evidence.json").unlink()
    result = _run(paths)
    assert result.returncode != 0
    assert "evidence" in result.stderr.lower()


def test_rejects_changed_input_hash(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    key = next(iter(scope["input_sha256"]))
    scope["input_sha256"][key] = "d" * 64
    _write_json(paths["scope"], scope)
    result = _run(paths)
    assert result.returncode != 0
