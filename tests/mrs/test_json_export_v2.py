"""JSON-export coverage for the 18 Study-2 expansion PUTs (90 cells).

Mirrors tests/mrs/test_json_export.py for the a4..d8 cohort. Primary MP follows
the deterministic PRIMARY_CELLS_V3 class rule (A→1, B→2, C→5, D→2).
"""
import json
from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent.parent / "data" / "mr_export"
PUTS = ["a4", "a5", "a6", "a7", "a8", "b4", "b5", "b6", "b7",
        "c4", "c5", "c6", "c7", "d4", "d5", "d6", "d7", "d8"]
PRIMARY = {"a4": 1, "a5": 1, "a6": 1, "a7": 1, "a8": 1,
           "b4": 2, "b5": 2, "b6": 2, "b7": 2,
           "c4": 5, "c5": 5, "c6": 5, "c7": 5,
           "d4": 2, "d5": 2, "d6": 2, "d7": 2, "d8": 2}


def test_all_90_files_exist():
    missing = []
    for put in PUTS:
        for k in range(1, 6):
            f = EXPORT_DIR / f"{put}_MP{k}_mr.json"
            if not f.exists():
                missing.append(f.name)
    assert not missing, f"Missing files: {missing}"


def test_primary_flag_correct():
    for put in PUTS:
        for k in range(1, 6):
            data = json.loads((EXPORT_DIR / f"{put}_MP{k}_mr.json").read_text())
            assert data["primary"] == (k == PRIMARY[put]), f"{put} MP{k}"


def test_sample_pairs_schema():
    for put in PUTS:
        for k in range(1, 6):
            data = json.loads((EXPORT_DIR / f"{put}_MP{k}_mr.json").read_text())
            assert len(data["sample_pairs"]) == 3
            for pair in data["sample_pairs"]:
                assert set(pair.keys()) == {"x", "r_x", "y_orig", "y_new", "holds"}
                assert isinstance(pair["holds"], bool)


def test_primary_mr_holds_on_samples():
    for put in PUTS:
        k = PRIMARY[put]
        data = json.loads((EXPORT_DIR / f"{put}_MP{k}_mr.json").read_text())
        fails = [p for p in data["sample_pairs"] if not p["holds"]]
        assert not fails, f"{put} MP{k} primary MR fails on: {fails}"
