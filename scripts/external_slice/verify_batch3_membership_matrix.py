#!/usr/bin/env python3
"""Verify Batch 3 membership byte-identity and A1d-r2 matrix binding."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_helpers():
    path = Path(__file__).resolve().parent / "batch3_a1d_r1.py"
    spec = importlib.util.spec_from_file_location("batch3_a1d_r1", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    helpers = _load_helpers()
    membership_path = ROOT / "data/external_slice/BATCH3_MEMBERSHIP.json"
    matrix_path = ROOT / "data/external_slice/BATCH3_EXECUTION_MATRIX.json"
    readiness_path = ROOT / "data/external_slice/readiness_batch3.json"
    sheet_path = ROOT / "data/external_slice/admission_sheet.csv"
    candidate_path = (
        ROOT / "data/external_slice/admission_sheet.cursor_candidate.csv"
    )
    repro_root = ROOT / "data/external_slice/reproduction"

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

    formal_seeds = [0, 1, 2, 3, 4]
    for case in readiness["cases"]:
        nid = case["neutral_id"]
        case_dir = repro_root / nid
        # Reconstruct all five formal seeds from hash-bound JSON + RC files.
        reconstructed = helpers.reconstruct_formal_per_seed_from_artifacts(
            case_dir, formal_seeds=formal_seeds
        )
        assert set(reconstructed) == set(formal_seeds), (
            f"{nid}: reconstructed seeds {sorted(reconstructed)} "
            f"!= {formal_seeds}"
        )
        aggregation = helpers.aggregate_formal_verdict(
            reconstructed, formal_seeds=formal_seeds
        )
        for seed in formal_seeds:
            row = next(r for r in aggregation["seed_rows"] if r["seed"] == seed)
            assert row["parity_ok"] is True or (
                case.get("proposed_crit_dual_arm_repro") != "PASS"
            )
            if case.get("proposed_crit_dual_arm_repro") == "PASS":
                assert row["seed_ok"] is True
                assert row["input_parity_ok"] is True
                assert row["buggy_property_holds"] is False
                assert row["fixed_property_holds"] is True
                assert row["buggy_raw_return_code"] == 1
                assert row["fixed_raw_return_code"] == 0

        reported = case.get("formal_aggregation") or {}
        assert reported.get("formal_seeds", formal_seeds) == formal_seeds
        assert (
            reported.get("proposed_crit_dual_arm_repro")
            == aggregation["proposed_crit_dual_arm_repro"]
            == case.get("proposed_crit_dual_arm_repro")
        )
        assert reported.get("failing_seeds") == aggregation["failing_seeds"]
        if case.get("proposed_crit_dual_arm_repro") == "PASS":
            assert aggregation.get("all_seeds_contrasted") is True
            assert reported.get("all_seeds_contrasted") is True

        matrix_path_case = case_dir / "REPETITION_MATRIX.json"
        matrix_payload = json.loads(matrix_path_case.read_text(encoding="utf-8"))
        matrix_agg = matrix_payload.get("aggregation") or {}
        assert (
            matrix_agg.get("proposed_crit_dual_arm_repro")
            == aggregation["proposed_crit_dual_arm_repro"]
        )
        assert matrix_agg.get("failing_seeds") == aggregation["failing_seeds"]

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
