"""Offline tests for scripts/compute_dualblind_delta.py (Study-2 Families A, B).

The script is fully testable WITHOUT Study-2 data: synthetic SMS pools are
constructed to exercise every registered decision branch of H2-1 and H2-2
(confirm / not-confirmed / bounded-null / under-recruited). scripts/ is not a
package, so the module is loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_dualblind_delta.py"


def _load():
    spec = importlib.util.spec_from_file_location("compute_dualblind_delta", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DBD = _load()
PRIMARY = DBD.PRIMARY
# a full 30-PUT grid split 7-8 per class per the registered expansion
PUTS = [p for p in PRIMARY]


def build_pool(per_put):
    """per_put: {put: (aligned_sms, [4 cross_sms])} -> 150-cell SMS dict."""
    pool = {}
    for put, (aligned, cross) in per_put.items():
        prim = PRIMARY[put]
        cross_iter = iter(cross)
        for mp in range(1, 6):
            key = f"{put.upper()}_MP{mp}"
            val = aligned if mp == prim else next(cross_iter)
            pool[key] = {"cell": key, "sms": float(val)}
    return pool


# --------------------------------------------------------------------------- #
# Cliff's delta + bootstrap primitives
# --------------------------------------------------------------------------- #
def test_cliffs_delta_dominance_and_ties():
    assert DBD.cliffs_delta([1, 1, 1], [0, 0, 0]) == 1.0
    assert DBD.cliffs_delta([0, 0], [1, 1]) == -1.0
    assert DBD.cliffs_delta([0.5, 0.5], [0.5, 0.5]) == 0.0
    assert DBD.cliffs_delta([], [1]) == 0.0


def test_vacant_and_dead_exclusion_rules():
    # vacant cell (flagged) excluded; dead PUT (sms=0) retained.
    assert DBD._is_excluded({"vacant": True, "sms": 0.5}) is True
    assert DBD._is_excluded({"adjudicated": False, "sms": 0.5}) is True
    assert DBD._is_excluded({"sms": None}) is True
    assert DBD._is_excluded({"sms": 0.0}) is False  # dead cell contributes zero
    assert DBD._is_excluded(None) is True


# --------------------------------------------------------------------------- #
# H2-1 decision branches (Family A)
# --------------------------------------------------------------------------- #
def test_h2_1_verdict_function_branches():
    assert DBD.verdict_h2_1(0.10)[0] == "CONFIRM"
    assert DBD.verdict_h2_1(0.0)[0] == "NOT_CONFIRMED"
    assert DBD.verdict_h2_1(-0.2)[0] == "NOT_CONFIRMED"


def test_h2_1_confirm_when_aligned_dominates():
    pool = build_pool({p: (0.9, [0.0, 0.0, 0.0, 0.0]) for p in PUTS})
    res = DBD.analyze_h2_1(pool, B=800, seed=DBD.MASTER_SEED)
    assert res["cliffs_delta"] > 0.9
    assert res["one_sided_95_lower_bound"] > 0
    assert res["verdict"] == "CONFIRM"
    # Romano band is descriptive-only and never a confirmatory pass.
    assert "descriptive_only" in res and "romano_band" in res["descriptive_only"]


def test_h2_1_not_confirmed_when_no_separation():
    pool = build_pool({p: (0.3, [0.3, 0.3, 0.3, 0.3]) for p in PUTS})
    res = DBD.analyze_h2_1(pool, B=800, seed=DBD.MASTER_SEED)
    assert res["one_sided_95_lower_bound"] <= 0
    assert res["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# H2-2 decision branches (Family B)
# --------------------------------------------------------------------------- #
def test_h2_2_verdict_function_branches():
    # CI excludes 0 -> CONFIRM
    assert DBD.verdict_h2_2(0.10, 0.30)[0] == "CONFIRM"
    assert DBD.verdict_h2_2(-0.30, -0.10)[0] == "CONFIRM"
    # CI includes 0, half-width <= 0.14 -> BOUNDED_NULL
    v, _, hw = DBD.verdict_h2_2(-0.10, 0.10)
    assert v == "BOUNDED_NULL" and hw <= DBD.DD_HALFWIDTH_BOUND
    # CI includes 0, half-width > 0.14 -> UNDER_RECRUITED
    v2, _, hw2 = DBD.verdict_h2_2(-0.30, 0.30)
    assert v2 == "UNDER_RECRUITED" and hw2 > DBD.DD_HALFWIDTH_BOUND


def test_h2_2_confirm_source_diversity_effect():
    # cross arm: strong aligned dominance; same arm: none -> large +Delta-delta,
    # consistent across all 30 PUTs -> tight CI excluding 0.
    cross = build_pool({p: (0.9, [0.0, 0.0, 0.0, 0.0]) for p in PUTS})
    same = build_pool({p: (0.3, [0.3, 0.3, 0.3, 0.3]) for p in PUTS})
    res = DBD.analyze_h2_2(cross, same, B=800, seed=DBD.MASTER_SEED)
    assert res["delta_delta_point"] > 0.5
    lo, hi = res["ci95_two_sided"]
    assert lo > 0  # CI excludes 0
    assert res["verdict"] == "CONFIRM"


def test_h2_2_bounded_null_when_arms_identical():
    # identical arms -> Delta-delta == 0 with a tight CI (half-width <= 0.14).
    per = {p: (0.8, [0.1, 0.2, 0.0, 0.3]) for p in PUTS}
    cross = build_pool(per)
    same = build_pool(per)
    res = DBD.analyze_h2_2(cross, same, B=800, seed=DBD.MASTER_SEED)
    assert res["delta_delta_point"] == 0.0
    assert res["ci95_half_width"] <= DBD.DD_HALFWIDTH_BOUND
    assert res["verdict"] == "BOUNDED_NULL"


def test_h2_2_under_recruited_with_few_heterogeneous_puts():
    # only 6 PUTs, heterogeneous per-arm deltas -> wide CI including 0.
    few = PUTS[:6]
    cross = build_pool({p: (0.9 if i % 2 else 0.1, [0.0, 0.9, 0.1, 0.5])
                        for i, p in enumerate(few)})
    same = build_pool({p: (0.1 if i % 2 else 0.9, [0.9, 0.0, 0.5, 0.1])
                       for i, p in enumerate(few)})
    res = DBD.analyze_h2_2(cross, same, B=800, seed=DBD.MASTER_SEED)
    lo, hi = res["ci95_two_sided"]
    assert lo < 0 < hi                                   # CI includes 0
    assert res["ci95_half_width"] > DBD.DD_HALFWIDTH_BOUND
    assert res["verdict"] == "UNDER_RECRUITED"


# --------------------------------------------------------------------------- #
# End-to-end run + integrity
# --------------------------------------------------------------------------- #
def test_run_writes_report_and_is_deterministic(tmp_path):
    cross = build_pool({p: (0.9, [0.0, 0.0, 0.0, 0.0]) for p in PUTS})
    same = build_pool({p: (0.3, [0.3, 0.3, 0.3, 0.3]) for p in PUTS})
    cp = tmp_path / "cross.json"
    sp = tmp_path / "same.json"
    op = tmp_path / "out.json"
    cp.write_text(json.dumps(cross))
    sp.write_text(json.dumps(same))
    r1 = DBD.run(cp, sp, op, B=400, seed=DBD.MASTER_SEED)
    r2 = DBD.run(cp, sp, None, B=400, seed=DBD.MASTER_SEED)
    assert op.exists()
    written = json.loads(op.read_text())
    assert written["H2_1_aligned_dominates_cross"]["verdict"] == "CONFIRM"
    # pure function of inputs + seed: identical results on re-run
    assert r1["H2_2_source_diversity_dual_blind"]["delta_delta_point"] == \
        r2["H2_2_source_diversity_dual_blind"]["delta_delta_point"]
    assert r1["master_seed"] == 20260708


def test_binds_registered_primary_v3_not_v3b():
    # §4: c-class stays MP5; v3b (c->MP1) is prohibited.
    assert PRIMARY["c1"] == 5 and PRIMARY["c4"] == 5
    assert DBD.MASTER_SEED == 20260708 and DBD.B_BOOT == 10000


def test_consumes_campaign_cell_schema():
    """The analysis reads the exact SMS-cell schema the campaign's SMS stage
    emits (evaluate_cell / sms_track2_*.json: a dict keyed by CELL with an
    'sms' field). Cross-references the shared registration seed with the
    campaign harness."""
    camp_spec = importlib.util.spec_from_file_location(
        "cross_source_campaign_dbd", ROOT / "scripts" / "cross_source_campaign.py")
    camp = importlib.util.module_from_spec(camp_spec)
    camp_spec.loader.exec_module(camp)
    # shared registration constant across generation + analysis legs
    assert camp.REGISTERED_SEED == DBD.MASTER_SEED
    # a minimal mock SSOT in the campaign's cell schema is consumable
    mock = {"A1_MP1": {"cell": "A1_MP1", "sms": 0.5, "inst": 6, "killed": 3}}
    aligned, cross = DBD.split_aligned_cross(mock)
    assert aligned == [0.5] and cross == []
