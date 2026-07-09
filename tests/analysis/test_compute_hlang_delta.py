"""Offline tests for scripts/compute_hlang_delta.py (Study-4 H-LANG, Family L).

Synthetic per-cell C-port SMS pools exercise every registered branch:
  * CONFIRM        : aligned (primary MP) SMS dominates cross -> delta_C > 0,
                     one-sided 95% lower bound > 0.
  * NOT_CONFIRMED  : aligned == cross (delta_C ~ 0) and reversed (cross > aligned,
                     delta_C < 0) -> lower bound <= 0.
  * grid restriction: only the 7 C PUTs enter (extra non-C cells ignored);
                      n_aligned = 7, n_cross = 28, n_puts = 7.
  * exclusions     : vacant / null-SMS cells dropped (shared _is_excluded).
  * missing input  : main() returns exit code 2 (no-data behaviour).
  * byte-identical : cliffs_delta / bootstrap IMPORTED from compute_dualblind_delta.

The bootstrap is the SAME multinomial two-sample scheme as the Study-2 H2-1'
scorer; seed 20260708 fixed, so runs are deterministic. scripts/ is not a
package -> module loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts" / "compute_hlang_delta.py"


def _load():
    spec = importlib.util.spec_from_file_location("compute_hlang_delta", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _load()
PRIMARY = {"a": 1, "b": 2, "c": 5}


def build_c_pool(aligned_sms, cross_sms, puts=None, extra=None):
    """{PUT_MPk: {"sms": v}} for the 7 C PUTs. The primary-MP cell gets
    ``aligned_sms``; the 4 non-primary cells get ``cross_sms``. ``extra`` merges
    additional raw cells (e.g. a non-C PUT, or a vacant cell)."""
    puts = puts or list(H.C_GRID_PUTS)
    pool = {}
    for put in puts:
        prim = PRIMARY[put[0]]
        for mp in range(1, 6):
            pool[f"{put.upper()}_MP{mp}"] = {
                "sms": aligned_sms if mp == prim else cross_sms}
    if extra:
        pool.update(extra)
    return pool


# --------------------------------------------------------------------------- #
# registered constants + imported (byte-identical) machinery
# --------------------------------------------------------------------------- #
def test_registered_constants():
    assert H.MASTER_SEED == 20260708
    assert H.B_BOOT == 10000
    assert H.C_GRID_PUTS == ("a1", "a2", "a3", "b1", "b2", "b3", "c2")
    assert len(H.C_GRID_PUTS) == 7


def test_bootstrap_imported_not_reimplemented():
    # the estimand + resampling are the SAME objects as the frozen H2-1' scorer.
    assert H.cliffs_delta is H._DBD.cliffs_delta
    assert H.boot_delta_distribution is H._DBD.boot_delta_distribution
    assert H._is_excluded is H._DBD._is_excluded
    from p2.config.primary import PRIMARY_CELLS_V3
    assert H.PRIMARY is PRIMARY_CELLS_V3


# --------------------------------------------------------------------------- #
# CONFIRM: aligned dominates cross -> delta_C > 0, lower bound > 0
# --------------------------------------------------------------------------- #
def test_confirm_aligned_dominates():
    rep = H.analyze_hlang(build_c_pool(0.8, 0.05))
    assert rep["n_aligned"] == 7
    assert rep["n_cross"] == 28
    assert rep["n_puts"] == 7
    assert rep["cliffs_delta_C"] == 1.0
    assert rep["one_sided_95_lower_bound"] > 0.0
    assert rep["verdict"] == "CONFIRM"
    assert rep["verdict_bool"] is True
    assert "LANGUAGE-INVARIANT" in rep["licensed_claim"]


# --------------------------------------------------------------------------- #
# NOT_CONFIRMED: aligned == cross -> delta_C == 0, lower bound <= 0
# --------------------------------------------------------------------------- #
def test_not_confirmed_no_separation():
    rep = H.analyze_hlang(build_c_pool(0.3, 0.3))
    assert rep["cliffs_delta_C"] == 0.0
    assert rep["one_sided_95_lower_bound"] <= 0.0
    assert rep["verdict"] == "NOT_CONFIRMED"
    assert rep["verdict_bool"] is False
    assert "falsification" in rep["licensed_claim"]


# --------------------------------------------------------------------------- #
# NOT_CONFIRMED: reversed (cross dominates aligned) -> delta_C < 0
# --------------------------------------------------------------------------- #
def test_not_confirmed_reversed_direction():
    rep = H.analyze_hlang(build_c_pool(0.05, 0.8))
    assert rep["cliffs_delta_C"] == -1.0
    assert rep["one_sided_95_lower_bound"] < 0.0
    assert rep["verdict"] == "NOT_CONFIRMED"


# --------------------------------------------------------------------------- #
# grid restriction: non-C cells are ignored; n stays 7/28
# --------------------------------------------------------------------------- #
def test_non_c_cells_ignored():
    # inject c1/d3 (NOT in the C grid) with extreme values; must not enter.
    extra = {f"C1_MP{mp}": {"sms": 0.99} for mp in range(1, 6)}
    extra.update({f"D3_MP{mp}": {"sms": 0.99} for mp in range(1, 6)})
    rep = H.analyze_hlang(build_c_pool(0.8, 0.05, extra=extra))
    assert rep["n_aligned"] == 7 and rep["n_cross"] == 28
    assert rep["n_puts"] == 7


# --------------------------------------------------------------------------- #
# exclusions: vacant / null-SMS cells dropped
# --------------------------------------------------------------------------- #
def test_excluded_cells_dropped():
    pool = build_c_pool(0.8, 0.05)
    pool["A1_MP1"] = {"sms": None}                 # null SMS -> excluded aligned
    pool["B2_MP1"] = {"sms": 0.05, "vacant": True}  # vacant cross -> excluded
    rep = H.analyze_hlang(pool)
    assert rep["n_aligned"] == 6                     # one aligned dropped
    assert rep["n_cross"] == 27                      # one cross dropped


# --------------------------------------------------------------------------- #
# missing input -> exit 2
# --------------------------------------------------------------------------- #
def test_missing_input_exit_2(monkeypatch, tmp_path):
    missing = tmp_path / "no_v7c.json"
    monkeypatch.setattr("sys.argv",
                        ["compute_hlang_delta.py", "--matrix", str(missing)])
    assert H.main() == 2


# --------------------------------------------------------------------------- #
# run writes the SSOT, is deterministic, and stamps the pre-freeze provenance
# --------------------------------------------------------------------------- #
def test_run_writes_and_is_deterministic(tmp_path):
    pool = build_c_pool(0.8, 0.05)
    ip = tmp_path / "sms_track2_v7c.json"
    op = tmp_path / "hlang_delta_v7c.json"
    ip.write_text(json.dumps(pool))
    r1 = H.run(ip, op)
    r2 = H.run(ip, None)
    assert op.exists()
    written = json.loads(op.read_text())
    assert written["artefact"] == "hlang_delta_v7c"
    assert written["master_seed"] == 20260708
    assert written["bootstrap_B"] == 10000
    assert written["H_LANG_cross_language_invariance"]["verdict"] == "CONFIRM"
    assert r1 == r2                                   # bootstrap seed fixed


def test_print_verdict_smoke(capsys):
    report = {"H_LANG_cross_language_invariance": H.analyze_hlang(
        build_c_pool(0.8, 0.05))}
    H._print_verdict(report)
    out = capsys.readouterr().out
    assert "H-LANG" in out and "VERDICT: CONFIRM" in out


def test_missing_input_prints_freeze_note(monkeypatch, tmp_path, capsys):
    missing = tmp_path / "no_v7c.json"
    monkeypatch.setattr("sys.argv",
                        ["compute_hlang_delta.py", "--matrix", str(missing)])
    assert H.main() == 2
    err = capsys.readouterr().err
    assert "No Study-4 C confirmatory data exists" in err
