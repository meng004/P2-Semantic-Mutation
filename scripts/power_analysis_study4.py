"""Study-4 pre-registration power / feasibility analysis (P2/P3 paper).

Study 4 registers THREE confirmatory families on fresh data that does not yet
exist, now that a live cross-vendor gateway makes the long-gated cross-vendor
contrast executable (four vendor lineages: claude-fable-5 / gpt-5.5 /
gemini-3.5-flash / grok-4.1->4.3; credentials in the gitignored .env):

  (A) H2-2  (cross-vendor dual-blind source diversity) — finally EXECUTABLE.
      Two API-served arms (same-source = claude-fable-5 all slots; cross-source
      = the 3-slot structure mapped to gpt-5.5 / gemini-3.5-flash / grok-4.1).
      Blinded review = claude-fable-5 on blinded packets for BOTH arms;
      arbitration = gpt-5.5. Estimand + decision rule = v1.1's H2-2 VERBATIM
      (paired-role bootstrap Delta-delta CI). This module RERUNS the v1.1 power
      calc for this instantiation: the effect-size DGP is unchanged (v4 hurdle),
      so the registered power reproduces v1.1's number; what changed is
      executability (cross-vendor credentials now exist), not the statistics.

  (B) H4'''-graded rich-class recruitment fix. Study-3 v6 detected only
      n_rich = 6 of the 15 rich-class (C7+D8) PUTs (h4_graded_v6.json), too thin
      for the graded bootstrap. Study 4 DOUBLES (multiplier swept) the per-
      operator slots on C/D PUTs in BOTH arms and POOLS the two arms
      (pre-declared pooling; up to 2*15 = 30 rich PUT-arm units). Binomial
      projection from the v6 per-PUT detection rate p0 = 6/15 gives the slot
      multiplier m with expected pooled n_rich >= 24 at >= 80% probability.

  (C) H-LANG (cross-language invariance) — the BOLD hypothesis. NOETHER derives
      MetaPatterns from operator-algebra invariants of the governing equations,
      NOT from surface syntax, so the semantic-mutation construct should be
      LANGUAGE-INVARIANT. On a C port of the 12 original Study-1 PUTs the
      aligned>cross direction should replicate: one-sided 95% bootstrap lower
      bound of delta_C > 0 (same estimand as H2-1', primary-MP rule mapped to
      the C cells). Powered at n = 12 from the Study-2 v5 DGP (observed
      delta = 0.4295, dualblind_delta_delta_v5.json); n = 12 gives less power
      than the n = 28 grid, reported honestly.

DGP calibration is design-from-prior-study (disclosed): the v4 hurdle DGP for
H2-2 (as v1.1), the v5 hurdle DGP for H-LANG (delta ~ 0.43), and the v6 rich
detection rate for H4'''. No Study-4 outcome exists or is used. No LLM / API
calls; pure resampling from committed SSOTs.

Master seed 20260708 (freeze-date seed convention retained).

Usage:
    PYTHONPATH=src python3 scripts/power_analysis_study4.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RESULTS = ROOT / "data" / "results"
OUT = RESULTS / "power_study4.json"

MASTER_SEED = 20260708
N_SIM = 2000            # matches the v1.0/v1.1 SMS-leg Monte-Carlo budget
ALPHA = 0.05

V5_MATRIX = RESULTS / "sms_track2_v5.json"
V6_GRADED = RESULTS / "h4_graded_v6.json"

# 28-PUT confirmatory roster (pilots a2,b4 removed), class balance 7/6/7/8.
CONFIRMATORY_PUTS = [
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
]
# 12 original Study-1 PUTs (the ASPIRATIONAL C-port grid registered in v1.0).
ORIGINAL_12 = ["a1", "a2", "a3", "b1", "b2", "b3",
               "c1", "c2", "c3", "d1", "d2", "d3"]
# ACHIEVED C-port grid (amendment v1.1). The port landed at 7/12 PUTs; the five
# sklearn/ML-library kernels (c1, c3, d1, d2, d3) could not be faithfully ported
# to pure C99 and are disclosed as excluded (docs/prereg_v2/C_PORT_SPEC.md §3).
# a2 is RETAINED confirmatory in the C grid (amendment v1.1 decision): the C-side
# data is fresh and no C outcome was ever seen at freeze; the Python {a2,b4}
# pilot firewall is a CODE-level firewall over the PYTHON confirmatory pools, and
# H-LANG is a DISTINCT C-port estimand (already argued in v1.0 §2c). Keeping a2
# maximises the achieved C grid at n=7 (vs n=6 if excluded).
C_GRID_7 = ["a1", "a2", "a3", "b1", "b2", "b3", "c2"]
C_GRID_N = 7                          # amendment v1.1 registered H-LANG n
RICH_CLASSES = ("c", "d")
PRIMARY_BY_CLASS = {"a": 1, "b": 2, "c": 5, "d": 2}  # PRIMARY_CELLS_V3


def _load_study2_module():
    spec = importlib.util.spec_from_file_location(
        "power_analysis_study2", ROOT / "scripts" / "power_analysis_study2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- #
# DGP calibration from a committed SMS pool (aligned/cross hurdle)
# --------------------------------------------------------------------------- #
def calibrate_hurdle(matrix_path: Path, puts: list) -> dict:
    """Reconstruct the aligned (j=k) / cross (j!=k) hurdle DGP from a committed
    SMS pool over `puts` under PRIMARY_CELLS_V3 — identical shape to
    power_analysis_study2.load_study1_sms_hurdle, but pool/roster parametrised."""
    sms = json.loads(matrix_path.read_text())
    aligned, cross = [], []
    for p in puts:
        cls = p[0]
        for mp in range(1, 6):
            key = f"{p.upper()}_MP{mp}"
            if key not in sms:
                continue
            v = sms[key].get("sms")
            if v is None:
                continue
            (aligned if mp == PRIMARY_BY_CLASS[cls] else cross).append(float(v))
    aligned = np.array(aligned)
    cross = np.array(cross)
    return {
        "aligned_nonzero_mag": aligned[aligned > 0],
        "cross_nonzero_mag": cross[cross > 0],
        "p_nonzero_aligned": float((aligned > 0).mean()),
        "p_nonzero_cross": float((cross > 0).mean()),
        "mean_aligned": float(aligned.mean()),
        "mean_cross": float(cross.mean()),
        "n_aligned_cells": int(aligned.size),
        "n_cross_cells": int(cross.size),
    }


# --------------------------------------------------------------------------- #
# (A) H2-2 — cross-vendor Delta-delta power (rerun v1.1 verbatim methodology)
# --------------------------------------------------------------------------- #
def power_h2_2(s2mod) -> dict:
    """Rerun v1.1's paired-role Delta-delta power on the v4 hurdle DGP. The
    effect-size DGP and paired-SE calibration are UNCHANGED from v1.1, so this
    reproduces the v1.1 number (dd=0.20 @ n=28 ~ 0.793). The instantiation change
    is executability (cross-vendor gateway), not the statistics."""
    dgp_v4 = s2mod.load_study1_sms_hurdle()
    grid = (12, 18, 24, 28, 30, 36)
    dd = s2mod.power_delta_delta(dgp_v4, n_puts=grid,
                                 delta_deltas=(0.10, 0.15, 0.20))
    return {
        "estimand": "Delta-delta = delta(cross-source) - delta(same-source), "
                    "paired on the 28 confirmatory PUTs; both arms API-served "
                    "(symmetric dual-blind protocol, no harness/API asymmetry)",
        "decision_rule": "v1.1 H2-2 VERBATIM: paired-role bootstrap 95% two-sided "
                         "CI (B=10,000, seed 20260708). CI excludes 0 -> CONFIRM "
                         ">=0.20 effect; CI includes 0 AND half-width <= 0.14 -> "
                         "BOUNDED NULL; else UNDER-RECRUITED.",
        "dgp_source": "data/results/sms_track2_v4.json (v4 hurdle DGP; unchanged "
                      "from v1.1 — power is effect-size driven, not vendor driven)",
        "registered_n": 28,
        "target_detectable_delta_delta": 0.20,
        "paired_se_by_n": dd["paired_se_by_n"],
        "calibrated_paired_rho": dd["calibrated_paired_rho"],
        "power_by_delta_delta": dd["power"],
        "power_dd020_at_n28": dd["power"]["dd_0.2"]["28"] if isinstance(
            dd["power"]["dd_0.2"], dict) and "28" in dd["power"]["dd_0.2"]
            else dd["power"]["dd_0.2"][28],
        "min_n_80pct": dd["min_n_80pct"],
        "note": "Marginal at n=28 (just below 0.80) exactly as disclosed in v1.1; "
                "honestly reported. The registered three-way rule already licenses "
                "an UNDER-RECRUITED verdict if the CI is wide, so no threshold is "
                "moved to manufacture power.",
    }


# --------------------------------------------------------------------------- #
# (B) H4''' — rich-class recruitment slot multiplier (binomial projection)
# --------------------------------------------------------------------------- #
def recruitment_multiplier() -> dict:
    """Pooled-arm binomial projection for the slot multiplier that lifts detected
    rich PUT-arm units to n_rich >= 24 with >= 80% probability.

    Calibration: Study-3 v6 detected n_rich = 6 of the 15 rich-class (C7+D8)
    confirmatory PUTs (h4_graded_v6.json). Per-PUT-per-arm detection probability
    p0 = 6/15. Doubling per-operator slots multiplies the independent detection
    opportunities: with slot multiplier m the per-PUT detect prob is
    p_m = 1 - (1-p0)^m (m independent baseline campaigns). Pooling BOTH Study-4
    arms gives N = 2*15 = 30 rich PUT-arm Bernoulli(p_m) units; detected pooled
    n_rich ~ Binomial(30, p_m). Register the smallest integer m with
    P(n_rich >= 24) >= 0.80 (and expected >= 24)."""
    graded = json.loads(V6_GRADED.read_text())
    n_rich_v6 = int(graded["H4pp_graded"]["n_rich"])          # 6 detected rich PUTs
    n_rich_roster = 15                                        # C7 + D8 rich PUTs
    p0 = n_rich_v6 / n_rich_roster                           # per-PUT-per-arm detect
    N_POOLED = 2 * n_rich_roster                              # 2 arms * 15 = 30
    TARGET = 24
    curve = {}
    for m in range(1, 8):
        p_m = 1.0 - (1.0 - p0) ** m
        exp = N_POOLED * p_m
        p_ge = float(1.0 - stats.binom.cdf(TARGET - 1, N_POOLED, p_m))
        curve[m] = {"per_put_detect_p_m": round(p_m, 4),
                    "expected_pooled_n_rich": round(exp, 2),
                    "P_n_rich_ge_24": round(p_ge, 4),
                    "meets_gate": bool(exp >= TARGET and p_ge >= 0.80)}
    chosen = next((m for m in range(1, 8) if curve[m]["meets_gate"]), None)
    return {
        "calibration_source": "data/results/h4_graded_v6.json (Study-3 v6 "
                              "detected n_rich; design-from-prior-study, "
                              "Study-4 outcomes unseen)",
        "n_rich_detected_v6": n_rich_v6,
        "n_rich_roster": n_rich_roster,
        "per_put_per_arm_detect_p0": round(p0, 4),
        "pooling": "PRE-DECLARED pooling of the two Study-4 arms; N_pooled = 2*15 = 30 "
                   "rich PUT-arm units",
        "projection_model": "p_m = 1 - (1-p0)^m (doubling slots = m independent "
                            "baseline detection campaigns); n_rich ~ Binom(30, p_m)",
        "target_n_rich": TARGET,
        "prob_gate": 0.80,
        "multiplier_curve": curve,
        "x2_sufficient": curve[2]["meets_gate"],
        "chosen_multiplier": chosen,
        "chosen_expected_pooled_n_rich": curve[chosen]["expected_pooled_n_rich"]
            if chosen else None,
        "chosen_P_ge_24": curve[chosen]["P_n_rich_ge_24"] if chosen else None,
        "cost_note": ("x2 is INSUFFICIENT (expected pooled n_rich %.1f, "
                      "P(>=24) %.2f). The registered multiplier is x%s, which "
                      "roughly %sx-es the C/D mutant-generation + blinded-review "
                      "budget on the 15 rich PUTs across both arms; A/B slots are "
                      "unchanged, so the whole-campaign cost rises well below %sx."
                      % (curve[2]["expected_pooled_n_rich"],
                         curve[2]["P_n_rich_ge_24"], chosen, chosen, chosen))
            if chosen else "no multiplier <=7 meets the gate",
    }


# --------------------------------------------------------------------------- #
# (C) H-LANG — cross-language invariance power at n=12 (v5 DGP, delta ~ 0.43)
# --------------------------------------------------------------------------- #
def power_hlang(s2mod) -> dict:
    """delta_C > 0 one-sided, DGP calibrated from the Study-2 v5 pool (observed
    aligned>cross delta = 0.4295). Reuses power_analysis_study2.power_cliffs
    verbatim (same estimand as H2-1').

    AMENDMENT v1.1. v1.0 registered n = 12 (the full original grid). The C port
    landed at 7/12 PUTs (C_PORT_SPEC §3: 5 sklearn kernels unportable), so the
    ACHIEVED confirmatory C grid is n = 7 (a2 retained; see C_GRID_7). Power is
    recomputed HONESTLY at the achieved n=7 (and n=6 as an a2-excluded
    sensitivity). The n=12/18/24/28 curve is preserved byte-for-byte from v1.0
    (same seed 20260708, same v5 DGP) by appending 6/7 to the end of the grid, so
    the amendment adds the achieved points without perturbing the prior ones."""
    dgp_v5 = calibrate_hurdle(V5_MATRIX, CONFIRMATORY_PUTS)
    # Grid order (12,18,24,28,6,7) preserves the v1.0 draws for 12..28 and
    # appends the achieved C-grid points 6,7 (RNG stream unchanged for 12..28).
    cliffs = s2mod.power_cliffs(dgp_v5, n_puts=(12, 18, 24, 28, 6, 7),
                                thresholds=(0.0, 0.147))
    pw = cliffs["power_by_threshold"]["delta_ref_0.0"]
    p7 = pw[C_GRID_N]                 # achieved C grid (a2 IN)
    p6 = pw[6]                        # a2-excluded sensitivity
    p12 = pw[12]                      # v1.0 registered (superseded)
    return {
        "hypothesis": "H-LANG: on the ACHIEVED C port of the original Study-1 grid "
                      "(n=7; 5 sklearn PUTs unportable, C_PORT_SPEC §3) the "
                      "aligned>cross direction replicates (delta_C > 0)",
        "estimand": "one-sided 95% percentile-bootstrap lower bound on Cliff's "
                    "delta (aligned j=k vs cross j!=k) > 0 — SAME estimand as "
                    "H2-1', primary-MP rule (PRIMARY_CELLS_V3) mapped to the C cells",
        "amendment": "v1.1 (2026-07-09): registered n 12 -> 7 (achieved C-port "
                     "intersection); a2 RETAINED confirmatory (fresh C data, no C "
                     "outcome seen; Python pilot firewall is code-level over "
                     "Python pools; H-LANG is a distinct C-port estimand, v1.0 "
                     "§2c). Power recomputed honestly at n=7.",
        "c_grid_roster": C_GRID_7,
        "c_grid_excluded": ["c1", "c3", "d1", "d2", "d3"],
        "c_grid_excluded_reason": "sklearn/ML-library kernels; no faithful pure-"
                                  "C99 port (optimiser non-portability + "
                                  "numpy-PCG64 training-design non-reproducibility"
                                  "), C_PORT_SPEC §3",
        "n_puts": C_GRID_N,
        "primary_mp_rule_c": {"a": 1, "b": 2, "c": 5},   # PRIMARY_CELLS_V3, C cells present
        "c_cells_total": C_GRID_N * 5,                    # 7 PUTs x 5 MP = 35 cells
        "c_cells_aligned": C_GRID_N,                      # 1 primary MP per PUT
        "c_cells_cross": C_GRID_N * 4,                    # 4 non-primary MP per PUT
        "dgp_source": "data/results/sms_track2_v5.json (Study-2 v5 aligned/cross "
                      "hurdle; observed delta = 0.4295, design-from-prior-study)",
        "v5_calibrated_true_delta": cliffs["true_delta_dgp"],
        "v5_dgp": {k: (round(v, 4) if np.isscalar(v) else None)
                   for k, v in dgp_v5.items()
                   if k in ("p_nonzero_aligned", "p_nonzero_cross",
                            "mean_aligned", "mean_cross")},
        "power_delta_gt0_at_n7": p7,
        "power_delta_gt0_at_n6_a2excluded": p6,
        "power_delta_gt0_at_n12_v1_0_superseded": p12,
        "power_by_n": {str(k): pw[k] for k in sorted(pw)},
        "well_powered_at_n7": bool(p7 >= 0.80),
        "note": "AMENDMENT v1.1: the achieved C grid is n=7, which gives LESS "
                "power than the n=12 v1.0 registration and than the Python n=28 "
                "grid — reported honestly, NO threshold moved. At the "
                "v5-calibrated delta~0.43 DGP the one-sided directional claim is "
                "%s at n=7 (power %.4f; a2-excluded n=6 sensitivity %.4f). This is "
                "BELOW the 0.80 target; H-LANG stays registered as confirmatory "
                "with the achieved power disclosed (the estimand is a DIRECTION "
                "claim, not a magnitude claim, and the true delta~0.43 keeps it "
                "decently powered). Had we wished to hit 0.80 we would have needed "
                "the unportable ML PUTs; we do not fabricate them." % (
                    "well-powered" if p7 >= 0.80 else "under-powered vs 0.80 "
                    "(decently powered for a direction claim)",
                    p7, p6),
    }


def main():
    s2mod = _load_study2_module()
    result = {
        "meta": {
            "purpose": "Study-4 pre-registration power/feasibility; frozen before "
                       "any Study-4 data generation.",
            "master_seed": MASTER_SEED, "n_sim": N_SIM, "alpha": ALPHA,
            "families": ["H2-2 cross-vendor Delta-delta", "H4''' rich-class "
                         "recruitment", "H-LANG cross-language invariance"],
            "dgp_sources": {
                "h2_2": "data/results/sms_track2_v4.json (v1.1 methodology verbatim)",
                "h4ppp": "data/results/h4_graded_v6.json (v6 rich detection rate)",
                "hlang": "data/results/sms_track2_v5.json (v5 delta~0.43)",
            },
            "amendment_v1_1": "2026-07-09: H-LANG registered n 12 -> 7 (achieved "
                              "C-port intersection; 5 sklearn PUTs unportable, "
                              "C_PORT_SPEC §3). a2 retained confirmatory. Power "
                              "recomputed honestly at n=7 (below 0.80, disclosed).",
            "numpy": np.__version__, "scipy": stats.__name__.split(".")[0],
            "no_llm_calls": True,
        },
        "a_h2_2_cross_vendor_delta_delta": power_h2_2(s2mod),
        "b_h4ppp_rich_recruitment": recruitment_multiplier(),
        "c_hlang_cross_language": power_hlang(s2mod),
    }
    OUT.write_text(json.dumps(result, indent=2))
    print("wrote", OUT.relative_to(ROOT))

    a = result["a_h2_2_cross_vendor_delta_delta"]
    print("\n[H2-2] Delta-delta=0.20 power @n28 =",
          a["power_by_delta_delta"]["dd_0.2"], "| decision rule = v1.1 verbatim")
    b = result["b_h4ppp_rich_recruitment"]
    print("[H4'''] p0 = %.3f (n_rich_v6=%d/15); x2 sufficient=%s; chosen multiplier = x%s "
          "(expected pooled n_rich %.1f, P(>=24)=%.2f)" % (
              b["per_put_per_arm_detect_p0"], b["n_rich_detected_v6"],
              b["x2_sufficient"], b["chosen_multiplier"],
              b["chosen_expected_pooled_n_rich"], b["chosen_P_ge_24"]))
    for m, row in b["multiplier_curve"].items():
        print("        x%s: p_m=%.3f  E[n_rich]=%.1f  P(>=24)=%.3f  gate=%s" % (
            m, row["per_put_detect_p_m"], row["expected_pooled_n_rich"],
            row["P_n_rich_ge_24"], row["meets_gate"]))
    c = result["c_hlang_cross_language"]
    print("[H-LANG] v5 true delta = %s | ACHIEVED C grid n=%d %s | "
          "power(delta>0) @n7 = %.4f (a2-excl n6 = %.4f) | well-powered@0.80=%s" % (
              c["v5_calibrated_true_delta"], c["n_puts"], c["c_grid_roster"],
              c["power_delta_gt0_at_n7"], c["power_delta_gt0_at_n6_a2excluded"],
              c["well_powered_at_n7"]))


if __name__ == "__main__":
    main()
