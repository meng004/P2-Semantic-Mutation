import json
from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent.parent / "data" / "mr_export"
PUTS = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3", "d1", "d2", "d3"]
PRIMARY = {"a1": 4, "a2": 1, "a3": 3, "b1": 2, "b2": 2, "b3": 1,
           "c1": 5, "c2": 5, "c3": 5, "d1": 2, "d2": 2, "d3": 2}


def test_all_60_files_exist():
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
            expected = (k == PRIMARY[put])
            assert data["primary"] == expected, f"{put} MP{k}: expected primary={expected}"


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
