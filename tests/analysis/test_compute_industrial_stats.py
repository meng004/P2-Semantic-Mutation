"""Offline tests for scripts/compute_industrial_stats.py (Study-2 Families C, D).

Synthetic per-case census fixtures exercise every registered decision branch:
Tier A confirmatory (n>=45) / under-recruited (n<45), Tier B kept separate,
H2-4 incidence confirm / not-confirm, and E-PETSC-004 completion handling. No
Study-2 data is required. scripts/ is not a package -> module loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_industrial_stats.py"
_POWER = ROOT / "data" / "results" / "power_study2.json"


def _load():
    spec = importlib.util.spec_from_file_location("compute_industrial_stats", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


IND = _load()


def mk_case(n=40, t1=20, b1=10, b2=8, a1=18,
            t1_face="DETECT", b1_face=0, tier="A"):
    return {
        "n_applied": n,
        "kills": {"T1": t1, "B1": b1, "B2": b2, "A1": a1},
        "face": {"t1": t1_face, "b1": b1_face, "b2": 0,
                 "a1a": "LOSE", "a1b": "LOSE"},
        "tier": tier,
    }


def census(cases: dict) -> dict:
    return {"artefact": "industrial_percase_v2", "cases": cases}


def write_census(tmp_path, cases: dict) -> Path:
    p = tmp_path / "percase_v2.json"
    p.write_text(json.dumps(census(cases)))
    return p


def make_ids(n, prefix="A-CASE"):
    return {f"{prefix}-{i:03d}": mk_case() for i in range(n)}


# --------------------------------------------------------------------------- #
# statistics kit
# --------------------------------------------------------------------------- #
def test_wilcoxon_all_zero_is_degenerate_null():
    w = IND.wilcoxon_stats([0.0, 0.0, 0.0])
    assert w["n_eff"] == 0 and w["p_normal_one_sided"] == 1.0


def test_holm_monotone_and_cliffs_delta():
    adj = IND.holm([0.01, 0.20, 0.04])
    assert adj[0] <= adj[2] <= adj[1]
    assert IND.cliffs_delta([1, 1], [0, 0]) == 1.0


# --------------------------------------------------------------------------- #
# tiering + E-PETSC-004 (§6)
# --------------------------------------------------------------------------- #
def test_partition_tiers_and_exclusions():
    cases = {"A-1": mk_case(tier="A"), "B-1": mk_case(tier="B"),
             "Z-0": mk_case(n=0)}  # no applied mutants -> excluded
    a, b, excl = IND.partition_tiers(cases)
    assert a == ["A-1"] and b == ["B-1"] and excl == ["Z-0"]


def test_epetsc004_complete_absent_partial():
    assert IND.epetsc004_status({"E-PETSC-004": mk_case(n=23)})["status"].startswith("complete")
    assert IND.epetsc004_status({})["present"] is False
    partial = IND.epetsc004_status({"E-PETSC-004": mk_case(n=0)})
    assert "results-partial" in partial["status"]


# --------------------------------------------------------------------------- #
# H2-3 confirmatory vs under-recruited (Family C)
# --------------------------------------------------------------------------- #
def test_h2_3_confirmatory_when_tier_a_ge_45(tmp_path):
    cases = make_ids(45)
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=300, seed=IND.BOOT_SEED)
    h3 = rep["H2_3_mutation_phase_dominance"]
    assert h3["confirmatory_regime"] is True
    assert h3["verdicts"]["T1>B1"] == "CONFIRM"
    assert "under_recruitment" not in h3


def test_h2_3_under_recruited_when_tier_a_lt_45(tmp_path):
    cases = make_ids(35)
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=300, seed=IND.BOOT_SEED)
    h3 = rep["H2_3_mutation_phase_dominance"]
    assert h3["confirmatory_regime"] is False
    assert h3["verdicts"]["T1>B1"] == "UNDER_RECRUITED"
    ap = h3["under_recruitment"]["achieved_n_power"]
    assert ap["achieved_n"] == 35
    assert ap["nearest_registered_grid_n"] == 35
    # robustness battery still computed (adequately powered under-recruitment)
    b = h3["robustness_battery_T1_gt_B1"]
    assert 0.0 <= b["monte_carlo_sign_flip_on_mean_diff"]["p_one_sided"] <= 1.0


def test_h2_3_degenerate_no_separation_not_confirmed(tmp_path):
    # T1 == B1 in every case -> all-zero diffs -> Wilcoxon null -> not confirmed
    cases = {f"A-{i:03d}": mk_case(t1=10, b1=10) for i in range(45)}
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=300, seed=IND.BOOT_SEED)
    h3 = rep["H2_3_mutation_phase_dominance"]
    assert h3["verdicts"]["T1>B1"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# H2-4 Fisher incidence, separate family D
# --------------------------------------------------------------------------- #
def test_h2_4_confirm_incidence_separation(tmp_path):
    # T1 detects all, B1 detects few -> Fisher one-sided significant
    cases = {f"A-{i:03d}": mk_case(t1_face="DETECT",
                                   b1_face=(1 if i < 3 else 0))
             for i in range(40)}
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=200, seed=IND.BOOT_SEED)
    h4 = rep["H2_4_detection_incidence"]
    assert h4["t1_detect"] == 40 and h4["b1_detect"] == 3
    assert h4["fisher_p_one_sided"] < 0.05
    assert h4["verdict"] == "CONFIRM"


def test_h2_4_not_confirmed_when_incidence_equal(tmp_path):
    cases = {f"A-{i:03d}": mk_case(t1_face="DETECT", b1_face=1) for i in range(40)}
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=200, seed=IND.BOOT_SEED)
    h4 = rep["H2_4_detection_incidence"]
    assert h4["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# Tier B sensitivity stratum kept separate (§6.5)
# --------------------------------------------------------------------------- #
def test_tier_b_never_pooled(tmp_path):
    cases = make_ids(35, prefix="A-CASE")
    cases.update({f"B-CASE-{i:03d}": mk_case(tier="B") for i in range(5)})
    p = write_census(tmp_path, cases)
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=200, seed=IND.BOOT_SEED)
    assert rep["census"]["tier_a_n"] == 35            # Tier B excluded from primary
    assert rep["census"]["tier_b_n"] == 5
    tb = rep["tier_b_sensitivity_stratum"]
    assert tb["n_cases"] == 5 and len(tb["case_ids"]) == 5
    assert "NEVER pooled" in tb["label"]
    assert rep["H2_3_mutation_phase_dominance"]["tier_a_n"] == 35


def test_tier_b_absent_reports_none(tmp_path):
    p = write_census(tmp_path, make_ids(35))
    rep = IND.run(p, _POWER, tmp_path / "out.json", B=200, seed=IND.BOOT_SEED)
    assert rep["tier_b_sensitivity_stratum"]["n_cases"] == 0


# --------------------------------------------------------------------------- #
# integrity: writes SSOT, deterministic, registered seed
# --------------------------------------------------------------------------- #
def test_run_writes_and_is_deterministic(tmp_path):
    p = write_census(tmp_path, make_ids(45))
    op = tmp_path / "stats.json"
    r1 = IND.run(p, _POWER, op, B=300, seed=IND.BOOT_SEED)
    r2 = IND.run(p, _POWER, None, B=300, seed=IND.BOOT_SEED)
    assert op.exists()
    assert IND.BOOT_SEED == 20260708
    assert r1["H2_3_mutation_phase_dominance"]["holm_family"][0]["holm_adjusted_p"] == \
        r2["H2_3_mutation_phase_dominance"]["holm_family"][0]["holm_adjusted_p"]
