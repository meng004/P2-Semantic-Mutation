"""Offline tests for scripts/compute_h4_graded.py --pooled (Study-4 §3.2, §7b).

The ADDITIVE two-arm pooled path; the frozen v6 default is byte-unchanged
(covered by test_compute_h4_graded.py). Synthetic per-cell SMS matrices for each
arm exercise every registered branch of the recruitment-gated pooled verdict:

  * CONFIRM                 : pooled n_rich >= 24 AND boot_lower_95 > 0.15.
  * MISATTRIBUTION_CONFIRMED: pooled n_rich >= 24 AND boot_lower_95 <= 0.15
                              (sharp construct-property reading, §3.2).
  * UNDER_RECRUITED         : pooled n_rich < 24 (gate; no threshold moved).
  * pooling                 : a rich PUT detected in BOTH arms contributes TWO
                              units (union of rich PUT-arm units).
  * pilot firewall          : {a2,b4} never enter (non-rich + excluded).
  * CLI                     : --pooled needs >=2 pools; missing pool -> exit 2;
                              default output is h4_graded_v7.json, NOT the frozen
                              v6 SSOT.

Flip machinery is the imported S5 audit (in-memory; category_from_filename parses
the filename). Bootstrap seed 20260708 fixed -> deterministic. scripts/ is not a
package -> module loaded by path.
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
PRIMARY = {"a": 1, "b": 2, "c": 5, "d": 2}
RICH = [p for p in G.CONFIRMATORY_PUTS if p[0] in ("c", "d")]      # 15 rich PUTs


def _fn(put, cat, idx):
    return f"m{idx:02d}_{put}_{cat}1_claude_a{idx:02d}.py"


def build_arm(detect_rich, s_val, extra=None):
    """One arm's 5-MP SMS matrix. Each PUT in ``detect_rich`` gets one detected
    mutant with s_m = ``s_val`` (1 = primary-only kill, 0 = off-primary kill).
    ``extra`` merges additional PUTs (e.g. the pilots)."""
    spec = {}
    for p in detect_rich:
        prim = PRIMARY[p[0]]
        off = 1 if prim != 1 else 2
        spec[p] = [(_fn(p, "OS", 0), {prim} if s_val == 1 else {off})]
    if extra:
        spec.update(extra)
    matrix = {}
    for put, muts in spec.items():
        for mp in range(1, 6):
            outs = [{"file": fn, "label": "KILLED" if mp in killed else "SURVIVE"}
                    for fn, killed in muts]
            key = f"{put.upper()}_MP{mp}"
            matrix[key] = {"cell": key, "sms": 0.1, "inst": len(muts),
                           "killed": sum(1 for o in outs if o["label"] == "KILLED"),
                           "outcomes": outs}
    return matrix


def _write_arms(tmp_path, arm_a, arm_b):
    pa = tmp_path / "same.json"
    pb = tmp_path / "cross.json"
    pa.write_text(json.dumps(arm_a))
    pb.write_text(json.dumps(arm_b))
    return pa, pb


# --------------------------------------------------------------------------- #
# registered constants (pooled)
# --------------------------------------------------------------------------- #
def test_pooled_registered_constants():
    assert G.POOLED_GATE == 24
    assert G.GRADED_THRESHOLD == 0.15
    assert G.N_BOOT == 10000 and G.MASTER_SEED == 20260708
    assert G.POOLED_OUT.name == "h4_graded_v7.json"


# --------------------------------------------------------------------------- #
# CONFIRM: 30 units (all 15 rich in both arms), s_m=1 -> lower > 0.15
# --------------------------------------------------------------------------- #
def test_pooled_confirm(tmp_path):
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 30
    assert r["recruitment_gate_met"] is True
    assert r["pooled_rich_mean_share"] == 1.0
    assert r["boot_lower_95"] > 0.15
    assert r["verdict"] == "CONFIRM"
    assert "GRADED attribution" in r["licensed_claim"]


# --------------------------------------------------------------------------- #
# MISATTRIBUTION_CONFIRMED: adequate n but low share
# --------------------------------------------------------------------------- #
def test_pooled_misattribution_confirmed(tmp_path):
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 0), build_arm(RICH, 0))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 30 and r["recruitment_gate_met"] is True
    assert r["pooled_rich_mean_share"] == 0.0
    assert r["boot_lower_95"] <= 0.15
    assert r["verdict"] == "MISATTRIBUTION_CONFIRMED"
    assert "construct property" in r["licensed_claim"]


# --------------------------------------------------------------------------- #
# UNDER_RECRUITED: pooled n_rich < 24 (gate; no threshold moved)
# --------------------------------------------------------------------------- #
def test_pooled_under_recruited(tmp_path):
    # 10 rich per arm -> 20 units < 24, even though every share is a perfect 1.0.
    pa, pb = _write_arms(tmp_path, build_arm(RICH[:10], 1), build_arm(RICH[:10], 1))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 20
    assert r["recruitment_gate_met"] is False
    assert r["verdict"] == "UNDER_RECRUITED"
    assert "no threshold moved" in r["licensed_claim"]


def test_pooled_under_recruited_boundary_23_vs_24(tmp_path):
    # 12 + 11 = 23 units -> UNDER; 12 + 12 = 24 -> gate met.
    pa, pb = _write_arms(tmp_path, build_arm(RICH[:12], 1), build_arm(RICH[:11], 1))
    assert G.analyze_graded_pooled([pa, pb])["verdict"] == "UNDER_RECRUITED"
    pa, pb = _write_arms(tmp_path, build_arm(RICH[:12], 1), build_arm(RICH[:12], 1))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 24 and r["recruitment_gate_met"] is True
    assert r["verdict"] == "CONFIRM"


# --------------------------------------------------------------------------- #
# pooling: a rich PUT detected in BOTH arms contributes TWO units
# --------------------------------------------------------------------------- #
def test_pooling_double_counts_both_arm_puts(tmp_path):
    # arm A detects c1..c7,d1..d8 (15); arm B detects the SAME 15 -> 30 units.
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 30
    per_arm = r["per_arm"]
    assert all(v["n_rich_detected"] == 15 for v in per_arm.values())
    # each rich PUT appears once per arm in the pooled units -> 2x per PUT id
    puts_in_units = [u["put"] for u in r["pooled_units"]]
    assert len(puts_in_units) == 30
    assert puts_in_units.count("C1") == 2


# --------------------------------------------------------------------------- #
# pilot firewall: {a2,b4} never enter the pooled statistic
# --------------------------------------------------------------------------- #
def test_pooled_pilot_firewall(tmp_path):
    extra = {"a2": [(_fn("a2", "CF", 0), {1, 2, 3})],   # non-rich, pilot
             "b4": [(_fn("b4", "TF", 0), {1, 2, 3, 4})]}
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 1, extra=extra),
                         build_arm(RICH, 1, extra=extra))
    r = G.analyze_graded_pooled([pa, pb])
    assert r["pooled_n_rich"] == 30                    # pilots not added
    assert r["pilot_puts_excluded"] == ["a2", "b4"]
    assert all(u["put"].lower() not in ("a2", "b4") for u in r["pooled_units"])


# --------------------------------------------------------------------------- #
# run_pooled writes h4_graded_v7.json with pooled_n_rich; deterministic
# --------------------------------------------------------------------------- #
def test_run_pooled_writes_and_deterministic(tmp_path):
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    op = tmp_path / "h4_graded_v7.json"
    r1 = G.run_pooled([pa, pb], op)
    r2 = G.run_pooled([pa, pb], None)
    assert op.exists()
    w = json.loads(op.read_text())
    assert w["artefact"] == "h4_graded_v7"
    assert w["generated_by"].endswith("--pooled")
    assert w["H4ppp_graded_pooled"]["pooled_n_rich"] == 30
    assert w["H4ppp_graded_pooled"]["verdict"] == "CONFIRM"
    assert r1 == r2                                    # bootstrap seed fixed


# --------------------------------------------------------------------------- #
# frozen v6 default path is byte-unchanged: run() still emits h4_graded_v6
# --------------------------------------------------------------------------- #
def test_frozen_v6_default_untouched(tmp_path):
    # a single-arm confirmatory run through the ORIGINAL path is unaffected.
    m = build_arm(RICH, 1)
    ip = tmp_path / "sms_track2_v6.json"
    op = tmp_path / "v6.json"
    ip.write_text(json.dumps(m))
    rep = G.run(ip, op)
    assert rep["artefact"] == "h4_graded_v6"
    assert "H4pp_graded" in rep and "H4pp_strict" in rep


# --------------------------------------------------------------------------- #
# CLI: --pooled needs >= 2 pools; missing pool -> exit 2; default out = v7
# --------------------------------------------------------------------------- #
def test_cli_pooled_needs_two(monkeypatch, tmp_path):
    pa, _ = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    monkeypatch.setattr("sys.argv",
                        ["compute_h4_graded.py", "--pooled", str(pa)])
    assert G.main() == 2


def test_cli_pooled_missing_input_exit_2(monkeypatch, tmp_path):
    pa, _ = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    missing = tmp_path / "nope.json"
    monkeypatch.setattr("sys.argv", ["compute_h4_graded.py", "--pooled",
                                     str(pa), str(missing)])
    assert G.main() == 2


def test_cli_pooled_default_out_is_v7_not_v6(monkeypatch, tmp_path):
    pa, pb = _write_arms(tmp_path, build_arm(RICH, 1), build_arm(RICH, 1))
    # patch the module OUT/POOLED_OUT to tmp so we don't touch real SSOTs
    monkeypatch.setattr(G, "OUT", tmp_path / "h4_graded_v6.json")
    monkeypatch.setattr(G, "POOLED_OUT", tmp_path / "h4_graded_v7.json")
    monkeypatch.setattr("sys.argv", ["compute_h4_graded.py", "--pooled",
                                     str(pa), str(pb),
                                     "--out", str(tmp_path / "h4_graded_v6.json")])
    # note: default --out equals OUT; pooled mode must redirect to POOLED_OUT.
    assert G.main() == 0
    assert (tmp_path / "h4_graded_v7.json").exists()
    assert not (tmp_path / "h4_graded_v6.json").exists()
