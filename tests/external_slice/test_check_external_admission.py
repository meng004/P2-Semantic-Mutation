from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_external_admission.py"
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
FULL_SHA = "a" * 40
FIXED_SHA = "b" * 40


def _write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


def _candidate_row(index: int) -> dict[str, str]:
    return {
        "neutral_id": f"EXT-project-{index:02d}",
        "repo": "owner/project",
        "issue_url": f"https://github.com/owner/project/issues/{index}",
        "buggy_sha": FULL_SHA,
        "fixed_sha": FIXED_SHA,
        "mechanism_sentence": "restores the returned numerical value for the reported input.",
        "crit_real_defect": "PASS",
        "crit_dual_arm_repro": "PENDING",
        "crit_in_scope": "PASS",
        "decision": "ADMIT_PENDING_REPRO",
        "exclusion_reason": "",
        "analysis_id": "",
    }


def _pilot_row(index: int) -> dict[str, str]:
    row = _candidate_row(index)
    row["neutral_id"] = f"EXT-pilot-{index:02d}"
    row["mechanism_sentence"] = "rescales prediction scores before numerical calibration."
    return row


def _write_valid_fixture(tmp_path: Path) -> tuple[Path, Path]:
    external = tmp_path / "data" / "external_slice"
    sheet = external / "admission_sheet.cursor_candidate.csv"
    rows = [_candidate_row(index) for index in range(1, 65)]
    _write_sheet(sheet, rows)
    _write_sheet(external / "admission_sheet.csv", [_pilot_row(i) for i in range(1, 10)])

    evidence_root = external / "admission_evidence"
    manifest_hash = hashlib.sha256(b"sanitized-manifest").hexdigest()
    source_manifest = external / "defect4mr_import" / "candidates_sanitized.json"
    source_manifest.parent.mkdir(parents=True)
    source_manifest.write_bytes(b"sanitized-manifest")
    for index, row in enumerate(rows, start=1):
        case_dir = evidence_root / row["neutral_id"]
        case_dir.mkdir(parents=True)
        payload = {
            "neutral_id": row["neutral_id"],
            "source_pool": "defect4mr_64",
            "source_index": index,
            "source_manifest_sha256": manifest_hash,
            "issue_url": row["issue_url"],
            "fix_url": f"https://github.com/owner/project/commit/{FIXED_SHA}",
            "buggy_sha": row["buggy_sha"],
            "fixed_sha": row["fixed_sha"],
            "criteria": {
                "real_defect": row["crit_real_defect"],
                "dual_arm_repro": row["crit_dual_arm_repro"],
                "in_scope": row["crit_in_scope"],
            },
            "rationales": {
                "real_defect": "The public issue identifies wrong numerical behaviour and the commit fixes it.",
                "dual_arm_repro": "No public same-trigger two-version execution record was available at admission.",
                "in_scope": "The changed callable maps numerical input to one numerical output.",
            },
            "evidence_urls": [
                row["issue_url"],
                f"https://github.com/owner/project/commit/{FIXED_SHA}",
            ],
            "mechanism_sentence": row["mechanism_sentence"],
        }
        (case_dir / "evidence.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
    return sheet, evidence_root


def _run(sheet: Path, evidence_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--sheet",
            str(sheet),
            "--evidence-root",
            str(evidence_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_accepts_64_row_candidate_and_separate_nine_row_pilot(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)

    result = _run(sheet, evidence_root)

    assert result.returncode == 0, result.stderr
    assert "64 Defect4MR candidate rows" in result.stdout
    assert "9 supplemental pilot rows" in result.stdout


def test_rejects_nonblank_analysis_alias(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["analysis_id"] = "premature-alias"
    _write_sheet(sheet, rows)

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "analysis_id must be blank" in result.stderr


def test_rejects_abbreviated_commit_sha(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["fixed_sha"] = "abc1234"
    _write_sheet(sheet, rows)

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "fixed_sha must be a full 40-character commit" in result.stderr


def test_rejects_dual_arm_pass_without_fixed_arm(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["crit_real_defect"] = "FAIL"
    rows[0]["crit_dual_arm_repro"] = "PASS"
    rows[0]["fixed_sha"] = ""
    rows[0]["decision"] = "EXCLUDED"
    rows[0]["exclusion_reason"] = "no identifiable public fix commit"
    _write_sheet(sheet, rows)

    evidence = evidence_root / rows[0]["neutral_id"] / "evidence.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload["criteria"]["real_defect"] = "FAIL"
    payload["criteria"]["dual_arm_repro"] = "PASS"
    payload["fixed_sha"] = ""
    payload["fix_url"] = ""
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "dual-arm PASS requires immutable buggy and fixed commits" in result.stderr


def test_rejects_category_encoded_or_missing_evidence_identity(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["neutral_id"] = "EXT-A-project-01"
    _write_sheet(sheet, rows)

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "neutral_id encodes a prohibited category prefix" in result.stderr


def test_rejects_dual_arm_pass_without_public_execution_record(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["crit_dual_arm_repro"] = "PASS"
    _write_sheet(sheet, rows)
    evidence = evidence_root / rows[0]["neutral_id"] / "evidence.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload["criteria"]["dual_arm_repro"] = "PASS"
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "dual-arm PASS requires public execution evidence for both arms" in result.stderr


def test_rejects_unbound_evidence_url(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    evidence = evidence_root / rows[0]["neutral_id"] / "evidence.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload["evidence_urls"] = ["not-a-public-url"]
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "evidence_urls must contain public HTTP(S) URLs" in result.stderr


def test_rejects_source_index_not_bound_to_candidate_row(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    first = evidence_root / "EXT-project-01" / "evidence.json"
    second = evidence_root / "EXT-project-02" / "evidence.json"
    first_payload = json.loads(first.read_text(encoding="utf-8"))
    second_payload = json.loads(second.read_text(encoding="utf-8"))
    first_payload["source_index"], second_payload["source_index"] = 2, 1
    first.write_text(json.dumps(first_payload, indent=2) + "\n", encoding="utf-8")
    second.write_text(json.dumps(second_payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "source_index must match candidate row position" in result.stderr


def test_rejects_mixed_source_manifest_hashes(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    evidence = evidence_root / "EXT-project-01" / "evidence.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload["source_manifest_sha256"] = "c" * 64
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "all evidence must bind the same source manifest" in result.stderr


def test_rejects_extra_files_in_evidence_tree(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    (evidence_root / "EXT-project-01" / "unexpected.txt").write_text(
        "unexpected", encoding="utf-8"
    )

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "case directory must contain only evidence.json" in result.stderr


def test_rejects_hidden_extra_csv_cell(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    lines = sheet.read_text(encoding="utf-8").splitlines()
    lines[1] += ",hidden"
    sheet.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "row width does not match exact header" in result.stderr


def test_rejects_prohibited_downstream_vocabulary_in_sheet(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    rows = list(csv.DictReader(sheet.open(newline="", encoding="utf-8")))
    rows[0]["mechanism_sentence"] = "mentions a prediction token."
    _write_sheet(sheet, rows)

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "prohibited downstream vocabulary in sheet" in result.stderr


def test_rejects_missing_sanitized_source_manifest(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    source_manifest = sheet.parent / "defect4mr_import" / "candidates_sanitized.json"
    source_manifest.unlink()

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "sanitized source manifest is required" in result.stderr


def test_rejects_dual_arm_object_when_criterion_is_not_pass(tmp_path: Path) -> None:
    sheet, evidence_root = _write_valid_fixture(tmp_path)
    evidence = evidence_root / "EXT-project-01" / "evidence.json"
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    payload["dual_arm_evidence"] = {"unvalidated": True}
    evidence.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = _run(sheet, evidence_root)

    assert result.returncode != 0
    assert "dual_arm_evidence is forbidden unless the criterion is PASS" in result.stderr
