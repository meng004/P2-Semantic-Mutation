"""Offline tests for scripts/compute_h4_graded.py (Study-3 H4''-graded + H4''-strict).

Synthetic per-cell SMS matrices exercise every registered branch:
  * H4''-graded: CONFIRM (pure primary kills) / NOT_CONFIRMED (mis-declared) /
    boundary (rich mean exactly at the 0.15 bar -> strict-inequality fails).
  * H4''-strict: CONFIRM (clean single-stratum) / NOT_CONFIRMED (clean-family
    multi-stratum leakage) / FAIL_SCREEN_NOOP (screen-smoke gate: zero matched).
  * missing input (exit 2), pilot exclusion ({a2,b4} firewall), malformed input.

The invariant-flip classification is the IMPORTED Study-1 S5 machinery
(p2.mutators.stratum_filter.audit_matrix, constrained=ALL_FAMILIES): a mutant
KILLED in >=k MP cells has flip==k. Primary MPs (PRIMARY_CELLS_V3): A->1, B->2,
C->5, D->2. scripts/ is not a package -> module loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_h4_graded.py"


def _load():
    spec = importlib.util.spec_from_file_location("compute_h4_graded", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _load()


# --------------------------------------------------------------------------- #
# fixture builder: control per-mutant kill-MPs -> flip counts -> s_m / purity
# --------------------------------------------------------------------------- #
def build_matrix(mutants, extra=None):
    """mutants: {put: [(filename, killed_mps_set), ...]} -> 5-MP SMS matrix.

    A mutant KILLED in >=2 MP cells has flip>=2 (multi-stratum). ``extra`` merges
    additional PUTs (e.g. the excluded pilots)."""
    spec = dict(mutants)
    if extra:
        spec.update(extra)
    matrix = {}
    for put, muts in spec.items():
        for mp in range(1, 6):
            outs = [{"file": fn, "label": "KILLED" if mp in killed else "SURVIVE"}
                    for fn, killed in muts]
            key = f"{put.upper()}_MP{mp}"
            n_kill = sum(1 for o in outs if o["label"] == "KILLED")
            matrix[key] = {"cell": key, "sms": 0.1, "inst": len(muts),
                           "killed": n_kill, "outcomes": outs}
    return matrix


def _fn(put, cat, idx):
    """A pool filename whose category parses via category_from_filename."""
    return f"m{idx:02d}_{put}_{cat}1_claude_a{idx:02d}.py"


def _bad_fn(put, idx):
    """A filename that does NOT parse to a known category (screen no-op fixture)."""
    return f"junk_{put}_{idx}.py"


PRIMARY = {"a": 1, "b": 2, "c": 5, "d": 2}
RICH = [p for p in G.CONFIRMATORY_PUTS if p[0] in ("c", "d")]
NONRICH = [p for p in G.CONFIRMATORY_PUTS if p[0] in ("a", "b")]


def rich_pool(share_num, share_den, clean_pure=True):
    """All 28 confirmatory PUTs. Rich (c,d) PUTs get ``share_num`` primary-only
    (s_m=1) + ``share_den-share_num`` off-primary (s_m=0) detected mutants, so
    each rich PUT mean == share_num/share_den. Non-rich PUTs get one clean
    single-stratum kill so strict has a populated (pure) clean pool."""
    out = {}
    for p in G.CONFIRMATORY_PUTS:
        prim = PRIMARY[p[0]]
        off = 1 if prim != 1 else 2
        if p in RICH:
            muts = []
            for i in range(share_num):
                muts.append((_fn(p, "OS", i), {prim}))            # s_m = 1
            for i in range(share_num, share_den):
                muts.append((_fn(p, "OS", i), {off}))             # s_m = 0
            out[p] = muts
        else:
            out[p] = [(_fn(p, "CE", 0), {prim if clean_pure else prim})]
    return out


# --------------------------------------------------------------------------- #
# registered constants + imported machinery
# --------------------------------------------------------------------------- #
def test_registered_constants():
    assert G.GRADED_THRESHOLD == 0.15
    assert G.STRICT_THRESHOLD == 0.90
    assert G.MASTER_SEED == 20260708
    assert G.N_BOOT == 10000
    assert G.ALPHA == 0.05
    assert G.RICH_CLASSES == ("c", "d")
    assert G.CLEAN_FAMILIES == ("CE", "HP", "CF")
    assert sorted(G.PILOT_PUTS) == ["a2", "b4"]
    assert len(G.CONFIRMATORY_PUTS) == 28
    assert "a2" not in G.CONFIRMATORY_PUTS and "b4" not in G.CONFIRMATORY_PUTS


def test_flip_machinery_is_imported_not_reimplemented():
    from p2.mutators import stratum_filter
    from p2.config import primary
    assert G.audit_matrix is stratum_filter.audit_matrix
    assert G.ALL_FAMILIES is stratum_filter.ALL_FAMILIES
    assert G.PRIMARY_CELLS_V3 is primary.PRIMARY_CELLS_V3


# end-to-end analysis helper -------------------------------------------------
def analyze(matrix):
    puts = G._confirmatory_puts_present(matrix)
    per_mutant, audit = G.flip_map(matrix, puts)
    return (G.analyze_graded(matrix, per_mutant),
            G.analyze_strict(matrix, per_mutant, audit))


# --------------------------------------------------------------------------- #
# H4''-graded — CONFIRM: pure primary kills on rich PUTs
# --------------------------------------------------------------------------- #
def test_graded_confirm_pure_primary_real():
    graded, _ = analyze(build_matrix(rich_pool(1, 1)))
    assert graded["n_rich"] == 15
    assert graded["rich_mean_share"] == 1.0
    assert graded["boot_lower_95"] > 0.15
    assert graded["verdict"] == "CONFIRM"
    assert "GRADED attribution" in graded["licensed_claim"]
    assert graded["per_class_share_mean"]["C"]["n_puts"] == 7
    assert graded["per_class_share_mean"]["D"]["n_puts"] == 8


# --------------------------------------------------------------------------- #
# H4''-graded — NOT_CONFIRMED: mis-declared kills (primary never in flipset)
# --------------------------------------------------------------------------- #
def test_graded_not_confirmed_misdeclared():
    graded, _ = analyze(build_matrix(rich_pool(0, 1)))  # all off-primary -> s_m=0
    assert graded["n_rich"] == 15
    assert graded["rich_mean_share"] == 0.0
    assert graded["boot_lower_95"] <= 0.15
    assert graded["verdict"] == "NOT_CONFIRMED"
    assert "NOT confirmed" in graded["licensed_claim"]


# --------------------------------------------------------------------------- #
# H4''-graded — BOUNDARY: mean exactly at 0.15 fails (strict inequality)
# --------------------------------------------------------------------------- #
def test_graded_boundary_at_threshold_fails():
    # 3/20 = 0.15 in every rich PUT -> zero-variance pool -> boot_lower == 0.15.
    graded, _ = analyze(build_matrix(rich_pool(3, 20)))
    assert graded["rich_mean_share"] == 0.15
    assert graded["boot_lower_95"] == 0.15
    assert graded["verdict"] == "NOT_CONFIRMED"      # 0.15 > 0.15 is False


def test_graded_boundary_just_above_confirms():
    # 4/20 = 0.20 in every rich PUT -> boot_lower == 0.20 > 0.15 -> CONFIRM.
    graded, _ = analyze(build_matrix(rich_pool(4, 20)))
    assert graded["rich_mean_share"] == 0.20
    assert graded["boot_lower_95"] == 0.20
    assert graded["verdict"] == "CONFIRM"


# --------------------------------------------------------------------------- #
# graded s_m arithmetic: an f-way co-flip contributes 1/f
# --------------------------------------------------------------------------- #
def test_graded_coflip_gives_one_over_f():
    # one c-PUT with a single mutant killed under {5 (primary), 2} -> s_m = 1/2
    m = build_matrix({"c1": [(_fn("c1", "TF", 0), {5, 2})]})
    puts = G._confirmatory_puts_present(m)
    per_mutant, _ = G.flip_map(m, puts)
    graded = G.analyze_graded(m, per_mutant)
    assert graded["per_put_share"]["C1"] == 0.5
    # a purely mis-declared 3-way co-flip (primary 5 absent) -> s_m = 0
    m2 = build_matrix({"d1": [(_fn("d1", "SI", 0), {1, 3, 4})]})  # primary 2 absent
    pm2, _ = G.flip_map(m2, G._confirmatory_puts_present(m2))
    g2 = G.analyze_graded(m2, pm2)
    assert g2["per_put_share"]["D1"] == 0.0


# --------------------------------------------------------------------------- #
# H4''-strict — CONFIRM: clean-family single-stratum, screen matched > 0
# --------------------------------------------------------------------------- #
def test_strict_confirm_clean_single_stratum():
    # every confirmatory PUT: 2 clean CE mutants killed in exactly one stratum.
    pool = {p: [(_fn(p, "CE", 0), {1}), (_fn(p, "HP", 1), {3})]
            for p in G.CONFIRMATORY_PUTS}
    _, strict = analyze(build_matrix(pool))
    assert strict["n_clean_detected"] == 56          # 28 PUTs x 2
    assert strict["purity"] == 1.0
    assert strict["cp_lower_95"] >= 0.90
    assert strict["n_screened_candidates"] > 0
    assert strict["screen_matched_gt_zero"] is True
    assert strict["verdict"] == "CONFIRM"
    assert "single-stratum purity holds" in strict["licensed_claim"]


# --------------------------------------------------------------------------- #
# H4''-strict — NOT_CONFIRMED: clean-family multi-stratum leakage
# --------------------------------------------------------------------------- #
def test_strict_not_confirmed_clean_multistratum():
    # half the clean CF mutants are double-flips (flip==2) -> purity ~0.5.
    pool = {}
    for p in G.CONFIRMATORY_PUTS:
        pool[p] = [(_fn(p, "CE", 0), {1}),          # single-stratum
                   (_fn(p, "CF", 1), {1, 2})]        # multi-stratum (flip 2)
    _, strict = analyze(build_matrix(pool))
    assert strict["purity"] == 0.5
    assert strict["cp_lower_95"] < 0.90
    assert strict["n_screened_candidates"] > 0
    assert strict["verdict"] == "NOT_CONFIRMED"
    assert "CF" in strict["licensed_claim"]
    assert strict["cf_screened_out"] == 28


# --------------------------------------------------------------------------- #
# H4''-strict — FAIL_SCREEN_NOOP: the registered screen-smoke gate
# --------------------------------------------------------------------------- #
def test_strict_screen_smoke_gate_fails_on_zero_match():
    # all mutant filenames fail category parsing -> n_screened_candidates == 0.
    pool = {p: [(_bad_fn(p, 0), {1})] for p in G.CONFIRMATORY_PUTS}
    _, strict = analyze(build_matrix(pool))
    assert strict["n_screened_candidates"] == 0
    assert strict["screen_matched_gt_zero"] is False
    assert strict["verdict"] == "FAIL_SCREEN_NOOP"
    assert "LOUD FAIL" in strict["licensed_claim"]
    assert "P8" in strict["licensed_claim"]


# --------------------------------------------------------------------------- #
# PILOT-EXCLUSION: {a2,b4} leakage cannot enter either statistic
# --------------------------------------------------------------------------- #
def test_pilot_puts_excluded_from_both():
    pool = {p: [(_fn(p, "CE", 0), {1}), (_fn(p, "HP", 1), {3})]
            for p in G.CONFIRMATORY_PUTS}
    # pilots drenched in clean-family double-flips that would tank strict purity
    # AND rich-looking mis-declared kills — must NOT count.
    extra = {"a2": [(_fn("a2", "CF", 0), {1, 2, 3})],
             "b4": [(_fn("b4", "TF", 0), {1, 2, 3, 4, 5})]}
    graded, strict = analyze(build_matrix(pool, extra=extra))
    assert "A2" not in graded["per_put_share"] and "B4" not in graded["per_put_share"]
    assert strict["purity"] == 1.0                   # pilot leakage excluded
    assert strict["verdict"] == "CONFIRM"
    assert graded["pilot_puts_excluded"] == ["a2", "b4"]
    assert strict["pilot_puts_excluded"] == ["a2", "b4"]


# --------------------------------------------------------------------------- #
# MALFORMED input rejected
# --------------------------------------------------------------------------- #
def test_malformed_cell_key_rejected(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"ZZZ": {"outcomes": []}}))
    with pytest.raises(ValueError, match="malformed SMS cell key"):
        G.load_matrix(p)


def test_malformed_outcome_rejected(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"C1_MP1": {"outcomes": [{"label": "KILLED"}]}}))
    with pytest.raises(ValueError, match="malformed outcome"):
        G.load_matrix(p)


# --------------------------------------------------------------------------- #
# MISSING-INPUT: main() returns exit code 2 (no-data behaviour)
# --------------------------------------------------------------------------- #
def test_missing_input_exit_2(monkeypatch, tmp_path):
    missing = tmp_path / "does_not_exist.json"
    monkeypatch.setattr("sys.argv",
                        ["compute_h4_graded.py", "--matrix", str(missing)])
    assert G.main() == 2


# --------------------------------------------------------------------------- #
# end-to-end run + integrity + deterministic bootstrap
# --------------------------------------------------------------------------- #
def test_run_writes_and_is_deterministic(tmp_path):
    m = build_matrix(rich_pool(1, 1))
    ip = tmp_path / "matrix.json"
    op = tmp_path / "out.json"
    ip.write_text(json.dumps(m))
    r1 = G.run(ip, op)
    r2 = G.run(ip, None)
    assert op.exists()
    written = json.loads(op.read_text())
    assert written["artefact"] == "h4_graded_v6"
    assert written["run_mode"] == "confirmatory"
    assert written["H4pp_graded"]["verdict"] == "CONFIRM"
    assert written["master_seed"] == 20260708
    assert r1 == r2                                  # bootstrap seed fixed
    assert r1["family_g"]["graded_verdict"] == "CONFIRM"


def test_pilot_smoke_marks_artefact_and_guards_ssot(tmp_path, monkeypatch):
    m = build_matrix(rich_pool(1, 1))
    ip = tmp_path / "sms_track2_v6_pilot.json"
    ip.write_text(json.dumps(m))
    rep = G.run(ip, tmp_path / "pilot_out.json", pilot_smoke=True)
    assert rep["artefact"] == "h4_graded_v6_PILOT_SMOKE"
    assert rep["run_mode"].startswith("PILOT-SMOKE")
    # main() refuses to overwrite the confirmatory SSOT from a pilot-smoke run
    monkeypatch.setattr("sys.argv", [
        "compute_h4_graded.py", "--matrix", str(ip), "--pilot-smoke",
        "--out", str(G.OUT)])
    assert G.main() == 2


def test_consumes_campaign_cell_schema():
    # audit machinery reads the same {file,label} outcome schema the campaign emits.
    mock = {f"C1_MP{mp}": {"cell": f"C1_MP{mp}", "sms": 0.1,
                           "outcomes": [{"file": _fn("c1", "TF", 0),
                                         "label": "KILLED" if mp in (5, 2) else "SURVIVE"}]}
            for mp in range(1, 6)}
    per_mutant, audit = G.flip_map(mock, ["C1"])
    fc, fl, cat = per_mutant[("C1", _fn("c1", "TF", 0))]
    assert fc == 2 and set(fl) == {2, 5} and cat == "TF"
    assert audit["n_screened_candidates"] == 1
