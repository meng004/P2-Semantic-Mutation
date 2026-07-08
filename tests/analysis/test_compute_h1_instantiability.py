"""Offline tests for scripts/compute_h1_instantiability.py (Study-2 H1', Family E).

The script is fully testable WITHOUT Study-2 data: synthetic admitted-pool SMS
matrices exercise every registered branch of H1' (met / not-met / boundary /
missing-cell / pilot-exclusion enforced / malformed input rejected). scripts/ is
not a package, so the module is loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_h1_instantiability.py"


def _load():
    spec = importlib.util.spec_from_file_location("compute_h1_instantiability", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H1 = _load()


# --------------------------------------------------------------------------- #
# fixture builder in the exact campaign SMS-cell schema
# --------------------------------------------------------------------------- #
def build_matrix(per_put_fam, n_each=5, equiv_files=None, extra_puts=None):
    """per_put_fam: {put: {family: n_mutants}} -> 5-MP SMS matrix (schema-faithful).

    equiv_files: set of filenames to label EQUIV in every cell.
    extra_puts: optional {put: {family: n}} for pilot / Study-1 PUTs.
    """
    equiv_files = equiv_files or set()
    spec = dict(per_put_fam)
    if extra_puts:
        spec.update(extra_puts)
    matrix = {}
    for put, fams in spec.items():
        files = []
        for fam, n in fams.items():
            for i in range(n):
                files.append(f"m{i:02d}_{put}_{fam}1_claude_a{i % 3:02d}.py")
        for mp in range(1, 6):
            outs = []
            for f in files:
                lab = "EQUIV" if f in equiv_files else "SURVIVE"
                outs.append({"file": f, "label": lab})
            key = f"{put.upper()}_MP{mp}"
            matrix[key] = {"cell": key, "sms": 0.1, "inst": len(files),
                           "killed": 0, "outcomes": outs}
    return matrix


def all_clear_spec(n_each=5):
    return {p: {fam: n_each for fam in H1.FAMILIES} for p in H1.CONFIRMATORY_PUTS}


# --------------------------------------------------------------------------- #
# registered constants bound correctly
# --------------------------------------------------------------------------- #
def test_registered_constants():
    assert H1.MIN_MUTANTS == 5 and H1.REG_M == 8 and H1.REG_X == 4
    assert H1.MASTER_SEED == 20260708
    assert len(H1.CONFIRMATORY_PUTS) == 28
    assert H1.PILOT_PUTS == frozenset({"a2", "b4"})
    assert set(H1.FAMILIES) == {"CE", "OS", "HP", "TF", "SI"}


def test_parse_family_matches_admission_regex():
    assert H1.parse_family("m01_a1_CE1_claude_a02.py") == "CE"
    assert H1.parse_family("m10_b2_CF1_deepseek_a03.py") == "CF"
    assert H1.parse_family("not_a_mutant.py") is None


# --------------------------------------------------------------------------- #
# MET branch: >=4/5 families clear >=8/28
# --------------------------------------------------------------------------- #
def test_h1_confirm_when_all_families_clear():
    m = build_matrix(all_clear_spec(5))
    res = H1.analyze_h1(m)
    assert res["n_families_clearing_bar"] == 5
    assert res["verdict"] == "CONFIRM"
    for fam in H1.FAMILIES:
        assert res["per_family"][fam]["puts_cleared"] == 28


# --------------------------------------------------------------------------- #
# NOT-MET branch: SI narrow (Study-1 1/6) stays below, and one more fails
# --------------------------------------------------------------------------- #
def test_h1_not_confirmed_when_only_three_families_clear():
    spec = {}
    for p in H1.CONFIRMATORY_PUTS:
        spec[p] = {"CE": 5, "OS": 5, "HP": 5, "TF": 2, "SI": 1}  # TF,SI below 5
    m = build_matrix(spec)
    res = H1.analyze_h1(m)
    assert res["per_family"]["SI"]["puts_cleared"] == 0
    assert res["per_family"]["TF"]["puts_cleared"] == 0
    assert res["n_families_clearing_bar"] == 3
    assert res["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# BOUNDARY: exactly the bar (>=5 mutants on exactly 8 PUTs, exactly 4 families)
# --------------------------------------------------------------------------- #
def test_h1_boundary_exactly_at_bar_confirms():
    spec = {}
    for i, p in enumerate(H1.CONFIRMATORY_PUTS):
        # CE/OS/HP/TF get 5 mutants on the first 8 PUTs only, else 4 (below bar);
        # SI always 4 (below). => 4 families clear exactly 8, SI clears 0.
        n = 5 if i < 8 else 4
        spec[p] = {"CE": n, "OS": n, "HP": n, "TF": n, "SI": 4}
    m = build_matrix(spec)
    res = H1.analyze_h1(m)
    for fam in ("CE", "OS", "HP", "TF"):
        assert res["per_family"][fam]["puts_cleared"] == 8  # exactly the M bar
        assert res["per_family"][fam]["clears_bar"] is True
    assert res["per_family"]["SI"]["clears_bar"] is False
    assert res["n_families_clearing_bar"] == 4
    assert res["verdict"] == "CONFIRM"

    # one fewer cleared PUT (7) flips CE below the bar -> only 3 families -> NOT
    spec["a1"]["CE"] = 4
    m2 = build_matrix(spec)
    res2 = H1.analyze_h1(m2)
    assert res2["per_family"]["CE"]["puts_cleared"] == 7
    assert res2["per_family"]["CE"]["clears_bar"] is False
    assert res2["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# EQUIVALENCE: equivalent mutants do NOT count toward the >=5 bar
# --------------------------------------------------------------------------- #
def test_h1_equivalent_mutants_excluded():
    spec = {p: {fam: 5 for fam in H1.FAMILIES} for p in H1.CONFIRMATORY_PUTS}
    # mark two CE mutants of PUT a1 equivalent -> a1 CE drops to 3 (< 5)
    equiv = {"m00_a1_CE1_claude_a00.py", "m01_a1_CE1_claude_a01.py"}
    m = build_matrix(spec, equiv_files=equiv)
    res = H1.analyze_h1(m)
    assert res["per_family"]["CE"]["per_put_nonequiv_count"]["a1"] == 3
    assert "a1" not in res["per_family"]["CE"]["cleared_put_ids"]


def test_h1_ledger_overrides_equivalence():
    spec = {p: {fam: 5 for fam in H1.FAMILIES} for p in H1.CONFIRMATORY_PUTS}
    m = build_matrix(spec)
    ledger = {"a1": {"m00_a1_HP1_claude_a00.py": {"equivalent": True}}}
    res = H1.analyze_h1(m, ledger)
    assert res["per_family"]["HP"]["per_put_nonequiv_count"]["a1"] == 4


# --------------------------------------------------------------------------- #
# PILOT-EXCLUSION enforced: a2/b4 present in the pool are dropped, not counted
# --------------------------------------------------------------------------- #
def test_h1_pilot_and_study1_puts_excluded():
    spec = all_clear_spec(5)
    # inject pilot PUTs a2, b4 and a spurious non-confirmatory PUT c9
    extra = {"a2": {fam: 9 for fam in H1.FAMILIES},
             "b4": {fam: 9 for fam in H1.FAMILIES},
             "c9": {fam: 9 for fam in H1.FAMILIES}}
    m = build_matrix(spec, extra_puts=extra)
    res = H1.analyze_h1(m)
    assert res["pilot_puts_seen_and_dropped"] == ["a2", "b4"]
    assert "c9" in res["non_confirmatory_puts_dropped"]
    # pilots never inflate a family count: a2/b4 absent from any cleared list
    for fam in H1.FAMILIES:
        assert "a2" not in res["per_family"][fam]["cleared_put_ids"]
        assert "b4" not in res["per_family"][fam]["cleared_put_ids"]


# --------------------------------------------------------------------------- #
# MISSING-CELL: a confirmatory PUT absent from the pool is reported
# --------------------------------------------------------------------------- #
def test_h1_missing_confirmatory_put_reported():
    spec = all_clear_spec(5)
    del spec["d8"]                       # drop one confirmatory PUT entirely
    m = build_matrix(spec)
    res = H1.analyze_h1(m)
    assert "d8" in res["confirmatory_puts_missing_from_pool"]
    assert res["n_confirmatory_puts_present"] == 27


# --------------------------------------------------------------------------- #
# MALFORMED input rejected
# --------------------------------------------------------------------------- #
def test_h1_malformed_cell_key_rejected(tmp_path):
    bad = {"NOTACELL": {"outcomes": []}}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="malformed SMS cell key"):
        H1.load_pool(p)


def test_h1_malformed_outcome_entry_rejected(tmp_path):
    bad = {"A1_MP1": {"outcomes": [{"file": "x.py"}]}}   # missing 'label'
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="malformed outcome"):
        H1.load_pool(p)


# --------------------------------------------------------------------------- #
# end-to-end run + integrity
# --------------------------------------------------------------------------- #
def test_h1_run_writes_report_and_is_deterministic(tmp_path):
    m = build_matrix(all_clear_spec(5))
    ip = tmp_path / "pool.json"
    op = tmp_path / "out.json"
    ip.write_text(json.dumps(m))
    r1 = H1.run(ip, op)
    r2 = H1.run(ip, None)
    assert op.exists()
    written = json.loads(op.read_text())
    assert written["H1_operator_instantiability"]["verdict"] == "CONFIRM"
    assert r1 == r2
    assert r1["master_seed"] == 20260708


def test_h1_consumes_campaign_cell_schema():
    """H1' reads the exact SMS-cell schema the packet-harness campaign emits."""
    camp_spec = importlib.util.spec_from_file_location(
        "cross_source_campaign_h1", ROOT / "scripts" / "cross_source_campaign.py")
    camp = importlib.util.module_from_spec(camp_spec)
    camp_spec.loader.exec_module(camp)
    assert camp.REGISTERED_SEED == H1.MASTER_SEED
    # a minimal cell in the campaign's schema is consumable by per_put_pool
    mock = {"A1_MP1": {"cell": "A1_MP1", "sms": 0.5, "inst": 1,
                       "outcomes": [{"file": "m00_a1_CE1_claude_a00.py",
                                     "label": "KILLED"}]}}
    pools = H1.per_put_pool(mock)
    assert pools["a1"]["m00_a1_CE1_claude_a00.py"]["family"] == "CE"
