#!/usr/bin/env python3
"""Verify Batch 3 membership byte-identity and A1d-r1 matrix binding."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    membership_path = ROOT / "data/external_slice/BATCH3_MEMBERSHIP.json"
    matrix_path = ROOT / "data/external_slice/BATCH3_EXECUTION_MATRIX.json"
    readiness_path = ROOT / "data/external_slice/readiness_batch3.json"
    sheet_path = ROOT / "data/external_slice/admission_sheet.csv"
    candidate_path = (
        ROOT / "data/external_slice/admission_sheet.cursor_candidate.csv"
    )

    membership = json.loads(membership_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    ids = [row["neutral_id"] for row in membership["members"]]
    expected = [
        "EXT-numpy-01",
        "EXT-scipy-01",
        "EXT-scikit-learn-01",
        "EXT-statsmodels-01",
        "EXT-statsmodels-02",
        "EXT-statsmodels-03",
    ]
    assert ids == matrix["members"] == expected
    mem_sha = hashlib.sha256(membership_path.read_bytes()).hexdigest()
    assert mem_sha == matrix["membership_sha256_expected"]
    assert mem_sha == readiness["frozen_membership_sha256"]
    assert matrix["smoke"]["seeds"] == [0]
    assert matrix["formal_repetitions"]["seeds"] == [0, 1, 2, 3, 4]
    assert readiness["smoke_seeds"] == [0]
    assert readiness["formal_seeds"] == [0, 1, 2, 3, 4]
    assert [case["neutral_id"] for case in readiness["cases"]] == ids
    for case in readiness["cases"]:
        aggregation = case.get("formal_aggregation") or {}
        assert aggregation.get("formal_seeds", [0, 1, 2, 3, 4]) == [
            0,
            1,
            2,
            3,
            4,
        ]
        if case.get("proposed_crit_dual_arm_repro") == "PASS":
            assert aggregation.get("all_seeds_contrasted") is True
    sheet_sha = hashlib.sha256(sheet_path.read_bytes()).hexdigest()
    assert sheet_sha == (
        "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a"
    )
    rows = list(csv.DictReader(sheet_path.open(encoding="utf-8")))
    assert all(
        row["crit_dual_arm_repro"] == "PENDING"
        for row in rows
        if row["neutral_id"] in set(ids)
    )
    candidates = list(csv.DictReader(candidate_path.open(encoding="utf-8")))
    assert all(row["crit_dual_arm_repro"] == "PENDING" for row in candidates)
    print("membership_matrix_ok", len(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
