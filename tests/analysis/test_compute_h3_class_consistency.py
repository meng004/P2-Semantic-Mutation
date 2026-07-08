"""Offline tests for scripts/compute_h3_class_consistency.py (Study-2 H3', Family E).

Synthetic per-cell SMS pools exercise every registered branch of H3' (met /
not-met / boundary / missing-cell / pilot-exclusion enforced / malformed input
rejected) plus the descriptive sign test and exploratory Friedman companions.
scripts/ is not a package -> module loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_h3_class_consistency.py"


def _load():
    spec = importlib.util.spec_from_file_location("compute_h3_class_consistency", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H3 = _load()
PRIMARY = H3.PRIMARY


# --------------------------------------------------------------------------- #
# fixture builder: per (put, mp) SMS, aligned = primary MP
# --------------------------------------------------------------------------- #
def build_pool(aligned_cross, extra_puts=None):
    """aligned_cross: {put: (aligned_sms, cross_sms)} -> 5-MP SMS matrix.

    The aligned cell gets aligned_sms; the other four MPs get cross_sms.
    extra_puts is merged in (used for pilot / Study-1 injection).
    """
    spec = dict(aligned_cross)
    if extra_puts:
        spec.update(extra_puts)
    matrix = {}
    for put, (a, c) in spec.items():
        prim = PRIMARY[put]
        for mp in range(1, 6):
            key = f"{put.upper()}_MP{mp}"
            matrix[key] = {"cell": key, "sms": float(a if mp == prim else c),
                           "inst": 5, "killed": 0, "outcomes": []}
    return matrix


def uniform_spec(a, c):
    return {p: (a, c) for p in H3.CONFIRMATORY_PUTS}


# --------------------------------------------------------------------------- #
# registered constants
# --------------------------------------------------------------------------- #
def test_registered_constants():
    assert H3.REG_POSITIVE_CLASSES == 3 and H3.N_CLASSES == 4
    assert H3.MASTER_SEED == 20260708
    assert len(H3.CONFIRMATORY_PUTS) == 28
    assert H3.CLASS_SIZES == {"a": 7, "b": 6, "c": 7, "d": 8}
    # binds the deterministic v3 primary rule, not v3b (§4)
    assert PRIMARY["c1"] == 5 and PRIMARY["c7"] == 5
    assert PRIMARY["a4"] == 1 and PRIMARY["d8"] == 2


# --------------------------------------------------------------------------- #
# MET: all four classes positive (aligned > cross) -> CONFIRM
# --------------------------------------------------------------------------- #
def test_h3_confirm_all_classes_positive():
    m = build_pool(uniform_spec(0.6, 0.1))
    res = H3.analyze_h3(m)
    assert res["n_classes_positive"] == 4
    assert res["verdict"] == "CONFIRM"
    for r in res["per_class"]:
        assert r["direction"] == "positive"


# --------------------------------------------------------------------------- #
# NOT-MET: two classes reversed -> only 2 positive -> NOT_CONFIRMED
# --------------------------------------------------------------------------- #
def test_h3_not_confirmed_when_two_classes_reverse():
    spec = uniform_spec(0.6, 0.1)
    for p in H3.CONFIRMATORY_PUTS:
        if p[0] in ("c", "d"):
            spec[p] = (0.1, 0.6)                 # reverse C and D
    m = build_pool(spec)
    res = H3.analyze_h3(m)
    assert res["n_classes_positive"] == 2
    assert res["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# BOUNDARY: exactly 3 of 4 positive (one class tie/negative) -> CONFIRM
# --------------------------------------------------------------------------- #
def test_h3_boundary_exactly_three_positive_confirms():
    spec = uniform_spec(0.6, 0.1)
    for p in H3.CONFIRMATORY_PUTS:
        if p[0] == "d":
            spec[p] = (0.2, 0.2)                 # class D exactly tie (not positive)
    m = build_pool(spec)
    res = H3.analyze_h3(m)
    d = next(r for r in res["per_class"] if r["class"] == "D")
    assert d["direction"] == "tie" and d["positive"] is False   # exact tie, not positive
    assert res["n_classes_positive"] == 3
    assert res["verdict"] == "CONFIRM"


def test_h3_verdict_function_branches():
    assert H3.verdict_h3(4)[0] == "CONFIRM"
    assert H3.verdict_h3(3)[0] == "CONFIRM"
    assert H3.verdict_h3(2)[0] == "NOT_CONFIRMED"
    assert H3.verdict_h3(0)[0] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# descriptive sign test + exploratory Friedman companions present
# --------------------------------------------------------------------------- #
def test_h3_descriptive_signtest_and_exploratory_friedman():
    m = build_pool(uniform_spec(0.6, 0.1))
    res = H3.analyze_h3(m)
    a = next(r for r in res["per_class"] if r["class"] == "A")
    st = a["descriptive_sign_test"]
    assert st["n_puts_positive"] == 7 and st["n_puts_nonzero_delta"] == 7
    assert st["one_sided_binomial_p"] is not None
    assert "DESCRIPTIVE" in st["note"]
    fr = res["friedman_across_mps_exploratory"]
    assert fr["computed"] is True and "exploratory" in fr["family"].lower()


def test_h3_friedman_degenerate_all_identical_not_computed():
    m = build_pool(uniform_spec(0.3, 0.3))    # every cell identical -> Friedman NA
    res = H3.analyze_h3(m)
    assert res["friedman_across_mps_exploratory"]["computed"] is False


# --------------------------------------------------------------------------- #
# PILOT-EXCLUSION enforced: a2/b4 present cannot alter class means
# --------------------------------------------------------------------------- #
def test_h3_pilot_puts_excluded():
    spec = uniform_spec(0.6, 0.1)
    # inject pilots with a REVERSED strong signal; must NOT be counted
    extra = {"a2": (0.0, 1.0), "b4": (0.0, 1.0)}
    m = build_pool(spec, extra_puts=extra)
    res = H3.analyze_h3(m)
    a = next(r for r in res["per_class"] if r["class"] == "A")
    b = next(r for r in res["per_class"] if r["class"] == "B")
    assert "a2" not in a["confirmatory_puts"]
    assert "b4" not in b["confirmatory_puts"]
    assert res["n_classes_positive"] == 4       # pilots did not flip direction
    assert res["verdict"] == "CONFIRM"


# --------------------------------------------------------------------------- #
# MISSING-CELL: a class computes on the available PUTs
# --------------------------------------------------------------------------- #
def test_h3_missing_puts_handled():
    spec = uniform_spec(0.6, 0.1)
    del spec["a8"]                               # drop one A PUT
    m = build_pool(spec)
    res = H3.analyze_h3(m)
    a = next(r for r in res["per_class"] if r["class"] == "A")
    assert "a8" not in a["confirmatory_puts"]
    assert a["direction"] == "positive"          # still computable


def test_h3_class_with_no_puts_reports_none():
    # only class B present -> A/C/D have no cells -> direction None, not positive
    spec = {p: (0.6, 0.1) for p in H3.CONFIRMATORY_PUTS if p[0] == "b"}
    m = build_pool(spec)
    res = H3.analyze_h3(m)
    a = next(r for r in res["per_class"] if r["class"] == "A")
    assert a["class_mean_aligned_sms"] is None and a["positive"] is False
    assert res["n_classes_positive"] == 1


# --------------------------------------------------------------------------- #
# vacant-cell exclusion (§7)
# --------------------------------------------------------------------------- #
def test_h3_vacant_cell_excluded():
    assert H3._is_excluded({"vacant": True, "sms": 0.5}) is True
    assert H3._is_excluded({"adjudicated": False, "sms": 0.5}) is True
    assert H3._is_excluded({"sms": None}) is True
    assert H3._is_excluded({"sms": 0.0}) is False


# --------------------------------------------------------------------------- #
# MALFORMED input rejected
# --------------------------------------------------------------------------- #
def test_h3_malformed_cell_key_rejected(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"WEIRD": {"sms": 0.1}}))
    with pytest.raises(ValueError, match="malformed SMS cell key"):
        H3.load_pool(p)


def test_h3_missing_sms_field_rejected(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"A1_MP1": {"cell": "A1_MP1"}}))
    with pytest.raises(ValueError, match="missing 'sms'"):
        H3.load_pool(p)


# --------------------------------------------------------------------------- #
# end-to-end run + integrity
# --------------------------------------------------------------------------- #
def test_h3_run_writes_and_is_deterministic(tmp_path):
    m = build_pool(uniform_spec(0.6, 0.1))
    ip = tmp_path / "pool.json"
    op = tmp_path / "out.json"
    ip.write_text(json.dumps(m))
    r1 = H3.run(ip, op)
    r2 = H3.run(ip, None)
    assert op.exists()
    assert json.loads(op.read_text())["H3_class_direction_consistency"]["verdict"] == "CONFIRM"
    assert r1 == r2
    assert r1["master_seed"] == 20260708


def test_h3_consumes_campaign_cell_schema():
    camp_spec = importlib.util.spec_from_file_location(
        "cross_source_campaign_h3", ROOT / "scripts" / "cross_source_campaign.py")
    camp = importlib.util.module_from_spec(camp_spec)
    camp_spec.loader.exec_module(camp)
    assert camp.REGISTERED_SEED == H3.MASTER_SEED
    mock = {f"A1_MP{mp}": {"cell": f"A1_MP{mp}", "sms": (0.5 if mp == 1 else 0.1)}
            for mp in range(1, 6)}
    sms = H3.per_put_sms(mock)
    assert sms["a1"][1] == 0.5 and sms["a1"][2] == 0.1
