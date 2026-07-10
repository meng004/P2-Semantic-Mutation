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
def recruitment_stratum_v1_2() -> dict:
    """AMENDMENT v1.2 (2026-07-09): pooled binomial projection for the dedicated
    harness-served RECRUITMENT STRATUM that lifts detected rich units to
    n_rich >= 24 with >= 0.90 probability.

    Serving-stack change (v1.2): the rich-class x4 EXTRA slots move OUT of the
    two H2-2 arms and into a SEPARATE claude-family recruitment stratum served by
    the session harness (no gateway quota). The two H2-2 arms therefore generate
    their rich cells at BASELINE (multiplier 1). Pre-declared pooling redefinition
    (before any Study-4 outcome exists):

        pooled rich units = same-arm rich baseline (15 @ p0)
                          + cross-arm rich baseline (15 @ p0)
                          + recruitment stratum       (15 @ p_ms)

    where p0 = 6/15 (v6 per-PUT-per-arm detect, unchanged calibration source),
    p_ms = 1 - (1-p0)^m_s (m_s independent harness detection passes per rich PUT),
    and the two arm baselines combine to Binomial(30, p0). n_rich is counted over
    all three groups (up to 45 PUT-source units); register the smallest integer
    m_s with P(pooled n_rich >= 24) >= 0.90. Because the arms are pinned at
    baseline, the pool's attainable P(>=24) ceiling is ~0.905 (arm mean 12 + at
    most 15 from a saturated stratum), so the gate is intrinsically tight and the
    registered m_s is a floor — disclosed, not moved. Single-family (claude)
    recruitment is disclosed: attribution structure (H4''') does not test vendor
    diversity, so a single generator lineage introduces no confound to the
    graded-share estimand."""
    graded = json.loads(V6_GRADED.read_text())
    n_rich_v6 = int(graded["H4pp_graded"]["n_rich"])          # 6 detected rich PUTs
    n_rich_roster = 15                                        # C7 + D8 rich PUTs
    p0 = n_rich_v6 / n_rich_roster                           # per-PUT-per-arm detect
    N_ARM_BASELINE = 2 * n_rich_roster                        # 2 arms * 15 baseline units
    N_POOLED = 3 * n_rich_roster                              # + stratum 15 -> 45 units
    TARGET = 24
    PROB_GATE = 0.90
    arm_pmf = stats.binom.pmf(np.arange(N_ARM_BASELINE + 1), N_ARM_BASELINE, p0)
    curve = {}
    for m in range(1, 16):
        p_ms = 1.0 - (1.0 - p0) ** m
        str_pmf = stats.binom.pmf(np.arange(n_rich_roster + 1), n_rich_roster, p_ms)
        pooled_pmf = np.convolve(arm_pmf, str_pmf)
        exp = N_ARM_BASELINE * p0 + n_rich_roster * p_ms
        p_ge = float(pooled_pmf[TARGET:].sum())
        curve[m] = {"stratum_per_put_detect_p_ms": round(p_ms, 4),
                    "expected_pooled_n_rich": round(exp, 2),
                    "P_n_rich_ge_24": round(p_ge, 4),
                    "meets_gate": bool(p_ge >= PROB_GATE)}
    chosen = next((m for m in range(1, 16) if curve[m]["meets_gate"]), None)
    ceiling = 15.0 + N_ARM_BASELINE * p0                      # saturated-stratum mean
    return {
        "amendment": "v1.2 (2026-07-09): recruitment-locus change only. The x4 "
                     "rich slots move OUT of the two H2-2 arms into a dedicated "
                     "harness-served claude-family recruitment stratum; arms "
                     "generate rich cells at BASELINE. No threshold, estimand, "
                     "decision rule, or seed changes.",
        "calibration_source": "data/results/h4_graded_v6.json (Study-3 v6 detected "
                              "n_rich; design-from-prior-study, Study-4 outcomes "
                              "unseen)",
        "serving_stack": "recruitment stratum = claude-family via session harness "
                         "(no gateway quota); H2-2 arms unchanged (same=harness "
                         "claude remainder, cross=gateway gpt-5.5/gemini-3.5-flash/"
                         "grok-4.1). Single-family stratum disclosed: H4''' "
                         "attribution does not test vendor diversity.",
        "n_rich_detected_v6": n_rich_v6,
        "n_rich_roster": n_rich_roster,
        "per_put_per_arm_detect_p0": round(p0, 4),
        "pooling": "PRE-DECLARED (v1.2): pooled = same-arm rich baseline (15@p0) + "
                   "cross-arm rich baseline (15@p0) + recruitment stratum (15@p_ms); "
                   "incl. any extra rich attempts already drawn in the caches "
                   "(drawn is drawn, nothing discarded); N_pooled up to 45 units.",
        "projection_model": "arms Binom(30,p0); stratum Binom(15, 1-(1-p0)^m_s); "
                            "pooled = arms (*) stratum (convolution); target n_rich "
                            ">= 24 at P >= 0.90",
        "target_n_rich": TARGET,
        "prob_gate": PROB_GATE,
        "attainable_ceiling_expected_pooled": round(ceiling, 2),
        "multiplier_curve": curve,
        "x4_sufficient": curve[4]["meets_gate"],
        "chosen_stratum_multiplier": chosen,
        "chosen_expected_pooled_n_rich": curve[chosen]["expected_pooled_n_rich"]
            if chosen else None,
        "chosen_P_ge_24": curve[chosen]["P_n_rich_ge_24"] if chosen else None,
        "operational_realization": (
            "the stratum is exported as 3 vendor-neutral harness slots x the "
            "registered attempts; the x4 that left the arms is the seed of the "
            "stratum's attempt budget, iterated to >= the registered floor of m_s "
            "independent detection passes per rich PUT. Harness-served, so the "
            "multiplier carries no gateway-quota cost."),
        "note": ("x4 alone is INSUFFICIENT under the v1.2 additive pooling "
                 "(P(>=24)=%.3f) because the two arms sit at baseline; the "
                 "registered stratum floor is m_s=x%s (P=%.3f, expected pooled "
                 "n_rich %.1f). The gate is tight (ceiling ~%.3f) and disclosed; "
                 "no threshold moved." % (
                     curve[4]["P_n_rich_ge_24"], chosen,
                     curve[chosen]["P_n_rich_ge_24"] if chosen else float("nan"),
                     curve[chosen]["expected_pooled_n_rich"] if chosen else float("nan"),
                     0.9054)) if chosen else "no multiplier <=15 meets the 0.90 gate",
    }


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


# --------------------------------------------------------------------------- #
# STUDY-5 EXTENSION (docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md)
# --------------------------------------------------------------------------- #
# ADDITIVE ONLY: invoked as `python3 scripts/power_analysis_study4.py --study5`;
# the default invocation (Study-4 power, power_study4.json) is byte-unchanged.
# Frozen before ANY Study-5 data generation (2026-07-10). DGP calibration is
# design-from-prior-study, stated openly: the v7c C-arm pool calibrates the
# primary H-LANG-2 DGP (observed delta_C = +0.2449, the Study-4 point
# estimate); the v7 Python cross-source arm calibrates the sensitivity DGP
# (observed delta = 0.4445); the v7 per-PUT SMS variance calibrates Family MR.
# No Study-5 outcome exists or is used. Master seed 20260708 retained.

OUT5 = RESULTS / "power_study5.json"
V7C_MATRIX = RESULTS / "sms_track2_v7c.json"
V7_CROSS_MATRIX = RESULTS / "sms_track2_v7.json"
V7_SAME_MATRIX = RESULTS / "sms_track2_v7_same.json"
N_SIM_STUDY5 = 10000            # registered Study-5 Monte-Carlo budget (B=10,000)
# Achieved-n lookup grid. 8/10/12 are the certification-attrition points the
# registration reports; 16..28 extend the SAME RNG stream (appended AFTER
# 8/10/12, so those draws are byte-preserved) to locate the min n reaching
# 0.80 under the deflated primary DGP — the Study-4 lesson (a knowingly
# under-powered n is design debt) applied prospectively.
HLANG2_N_GRID = (8, 10, 12, 16, 20, 24, 28)
MR_EFFECTS = (0.02, 0.05, 0.10, 0.20)
MR_RHO_GRID = (0.0, 0.5, 0.75)  # + the v7-calibrated rho appended at run time


def _per_put_mean_sms(matrix_path: Path, puts: list) -> dict:
    """{put: mean SMS over the PUT's non-null cells} (per-PUT battery-level
    SMS, the Family-MR unit statistic)."""
    sms = json.loads(matrix_path.read_text())
    vals: dict[str, list] = {}
    for cell, v in sms.items():
        put = cell.split("_")[0].lower()
        if put not in puts or not isinstance(v, dict):
            continue
        if v.get("vacant") is True or v.get("adjudicated") is False:
            continue
        if v.get("sms") is None:
            continue
        vals.setdefault(put, []).append(float(v["sms"]))
    return {p: float(np.mean(xs)) for p, xs in vals.items()}


def power_study5_hlang2(s2mod) -> dict:
    """Family XL (H-LANG-2, cross-language EXTERNAL corpus): direction power
    (delta_XL > 0, one-sided 95% bootstrap lower bound) on a target grid of
    n = 12 certified program-language pairs (each pair contributes 1 aligned
    + 4 cross cells, exactly the PUT-grid design), with achieved-n lookup
    points at n=10 and n=8 in case the registered §2c certification gate
    excludes pairs. SAME simulation machinery as power_study4.json's H-LANG
    entry (power_analysis_study2.power_cliffs; n_aligned=n, n_cross=4n; inner
    bootstrap 400), run at the registered Study-5 MC budget n_sim=10,000.

    Two DGPs, both design-from-prior-study:
      PRIMARY    : v7c C-arm hurdle (the Study-4 C-port pool; observed
                   delta_C = +0.2449 — the honest, deflated post-Study-4
                   effect assumption);
      SENSITIVITY: v7 Python cross-source-arm hurdle (observed delta =
                   0.4445 — the Python-scale effect, IF language costs
                   nothing)."""
    dgp_v7c = calibrate_hurdle(V7C_MATRIX, list(C_GRID_7))
    dgp_v7py = calibrate_hurdle(V7_CROSS_MATRIX, CONFIRMATORY_PUTS)
    legs = {}
    for tag, dgp, src, obs in (
            ("primary_v7c_cport", dgp_v7c,
             "data/results/sms_track2_v7c.json (Study-4 C-arm pool)", 0.2449),
            ("sensitivity_v7_python_arm", dgp_v7py,
             "data/results/sms_track2_v7.json (Study-4 Python cross arm)",
             0.4445)):
        cliffs = s2mod.power_cliffs(dgp, n_puts=HLANG2_N_GRID, thresholds=(0.0,))
        pw = cliffs["power_by_threshold"]["delta_ref_0.0"]
        legs[tag] = {
            "dgp_source": src,
            "observed_delta_calibration_anchor": obs,
            "dgp_true_delta": cliffs["true_delta_dgp"],
            "dgp": {k: round(v, 4) for k, v in dgp.items()
                    if k in ("p_nonzero_aligned", "p_nonzero_cross",
                             "mean_aligned", "mean_cross")},
            "power_delta_gt0_by_n": {str(n): pw[n] for n in HLANG2_N_GRID},
            "min_n_80pct": cliffs["min_n_80pct"]["delta_ref_0.0"],
        }
    p12 = legs["primary_v7c_cport"]["power_delta_gt0_by_n"]["12"]
    return {
        "family": "XL — H-LANG-2 cross-language invariance on an EXTERNAL "
                  "corpus of certified program-language pairs (single test, "
                  "confirmatory; the Study-4 Family-L NOT_CONFIRMED verdict "
                  "stands as recorded)",
        "estimand": "one-sided 95% percentile-bootstrap lower bound on Cliff's "
                    "delta_XL (aligned j=k vs cross j!=k) > 0; per-pair primary "
                    "stratum from the frozen XL roster category->stratum map "
                    "(configs/xl_roster.json, data-independent, frozen "
                    "pre-mutant); n pairs -> 5n cells, aligned n, cross 4n",
        "machinery": "power_analysis_study2.power_cliffs (identical to the "
                     "power_study4.json H-LANG entry), n_sim=10,000, inner "
                     "bootstrap 400, master seed 20260708",
        "registered_target_n": 12,
        "achieved_n_rule": "if the §2c certification gate excludes pairs, the "
                           "achieved power is READ OFF this frozen n=12/10/8 "
                           "curve — no post-data simulation",
        "n_sim": N_SIM_STUDY5,
        "legs": legs,
        "power_primary_at_n12": p12,
        "well_powered_at_n12_primary": bool(p12 >= 0.80),
        "note": "The primary DGP deliberately assumes the DEFLATED Study-4 "
                "C-arm point estimate (+0.2449), not the Python-scale effect: "
                "after the H-LANG NOT_CONFIRMED, powering the re-test on the "
                "optimistic Python effect would repeat the Study-4 design "
                "debt. Both legs are reported; the primary leg governs the "
                "§4 feasibility statement.",
    }


def power_study5_mr() -> dict:
    """Family MR (H2-4): paired per-PUT battery-level SMS difference
    delta_MR = SMS_R - SMS_L on the frozen v7 pools, n = 28 PUTs.

    Calibration (v7 SMS variance, design-from-prior-study): sigma_put = SD of
    the arm-averaged per-PUT mean SMS across the 28 confirmatory PUTs of the
    two frozen Study-4 arms; the between-arm per-PUT correlation calibrates
    the pairing rho ceiling. The R-vs-L pairing correlation on IDENTICAL
    frozen pools is unknown pre-data, so power is reported over a rho grid
    {0.0, 0.5, 0.75, rho_v7} — rho=0.0 is the worst-case (independent
    batteries) floor. sigma_d = sigma_put * sqrt(2*(1-rho)); SE = sigma_d /
    sqrt(28); one-sided z at alpha=0.05 (the same normal-approximation MC as
    power_delta_delta), 40,000 draws per design point, seed 20260708+5."""
    rng = np.random.default_rng(MASTER_SEED + 5)
    mc = _per_put_mean_sms(V7_CROSS_MATRIX, CONFIRMATORY_PUTS)
    ms = _per_put_mean_sms(V7_SAME_MATRIX, CONFIRMATORY_PUTS)
    common = [p for p in CONFIRMATORY_PUTS if p in mc and p in ms]
    x = np.array([mc[p] for p in common])
    y = np.array([ms[p] for p in common])
    avg = (x + y) / 2.0
    sigma_put = float(avg.std(ddof=1))
    rho_v7 = float(np.corrcoef(x, y)[0, 1])
    n = len(common)
    zcrit = stats.norm.ppf(1 - ALPHA)          # one-sided CONFIRM test
    zcrit2 = stats.norm.ppf(1 - ALPHA / 2)     # two-sided CI half-width
    rho_grid = tuple(MR_RHO_GRID) + (round(rho_v7, 4),)
    power = {}
    for rho in rho_grid:
        sigma_d = sigma_put * np.sqrt(2.0 * (1.0 - rho))
        se = sigma_d / np.sqrt(n)
        row = {"sigma_d": round(float(sigma_d), 4), "se_n28": round(float(se), 4),
               "projected_ci95_half_width": round(float(zcrit2 * se), 4),
               "meets_eq_halfwidth_0.14": bool(zcrit2 * se <= 0.14),
               "power_confirm_by_effect": {}}
        for eff in MR_EFFECTS:
            draws = rng.normal(eff, se, size=40000)
            row["power_confirm_by_effect"][f"d_{eff}"] = round(
                float((draws / se > zcrit).mean()), 4)
        power[f"rho_{rho}"] = row
    return {
        "family": "MR — H2-4 MR-side diversity (delta_MR = SMS_R - SMS_L, "
                  "paired on 28 PUTs, frozen v7 pools)",
        "calibration_source": "data/results/sms_track2_v7.json + "
                              "sms_track2_v7_same.json (v7 per-PUT SMS "
                              "variance; design-from-prior-study, no Study-5 "
                              "outcome exists)",
        "n_puts": n,
        "per_put_mean_sms": {"cross_arm_mean": round(float(x.mean()), 4),
                             "same_arm_mean": round(float(y.mean()), 4),
                             "arm_avg_sd_sigma_put": round(sigma_put, 4),
                             "between_arm_rho_v7": round(rho_v7, 4)},
        "machinery": "normal-approximation MC (same family as "
                     "power_delta_delta), 40,000 draws/design point, seed "
                     "20260708+5; sigma_d = sigma_put*sqrt(2(1-rho))",
        "effects_grid": list(MR_EFFECTS),
        "rho_grid": list(rho_grid),
        "power": power,
        "note": "Even at the worst-case rho=0.0 the projected two-sided CI "
                "half-width is far below the registered 0.14 equivalence "
                "gate, so the H2-4 ladder will effectively be decided by "
                "whether the CI includes 0 — disclosed in the registration "
                "(§3.4, §4); the 0.14 gate is kept verbatim for form-identity "
                "with H2-2 and NOT tightened post-hoc.",
    }


def power_study5_os(s2mod) -> dict:
    """Family OS (H2-3): identical estimand + three-way rule as H2-2, so the
    registered power RERUNS the v1.1/Study-4 methodology VERBATIM (v4 hurdle
    DGP, paired-role Delta-delta; seed stream identical) — what changes is the
    manipulated variable (open-spec vs registered-spec prompts), not the
    statistics."""
    dgp_v4 = s2mod.load_study1_sms_hurdle()
    dd = s2mod.power_delta_delta(dgp_v4, n_puts=(12, 18, 24, 28, 30, 36),
                                 delta_deltas=(0.10, 0.15, 0.20))
    return {
        "family": "OS — H2-3 open-specification source diversity "
                  "(Delta-delta_OS = delta(open-spec arm) - "
                  "delta(registered-spec arm), paired on 28 PUTs)",
        "decision_rule": "v1.1 H2-2 VERBATIM three-way (CONFIRM >= 0.20 / "
                         "BOUNDED_NULL half-width <= 0.14 / UNDER-RECRUITED)",
        "dgp_source": "data/results/sms_track2_v4.json (v4 hurdle DGP — "
                      "IDENTICAL to the v1.1 and Study-4 H2-2 power runs; "
                      "power is effect-size driven, not prompt driven)",
        "registered_n": 28,
        "target_detectable_delta_delta": 0.20,
        "paired_se_by_n": dd["paired_se_by_n"],
        "calibrated_paired_rho": dd["calibrated_paired_rho"],
        "power_by_delta_delta": dd["power"],
        "power_dd020_at_n28": dd["power"]["dd_0.2"][28],
        "min_n_80pct": dd["min_n_80pct"],
        "empirical_anchor_study4": "the Study-4 H2-2 achieved paired CI "
                                   "half-width was 0.0448 "
                                   "(dualblind_delta_delta_v7.json) — well "
                                   "inside the 0.14 BOUNDED_NULL gate; the "
                                   "projection above is therefore "
                                   "conservative",
        "note": "Marginal at n=28 (just below 0.80) exactly as in v1.1 and "
                "Study 4; the three-way rule already licenses UNDER-RECRUITED "
                "when the CI is wide, so no threshold is moved.",
    }


def main_study5():
    s2mod = _load_study2_module()
    # Registered Study-5 MC budget (set AFTER exec_module, per the module-
    # attribute trap noted in CLAUDE.md §4): n_sim 2000 -> 10000.
    s2mod.N_SIM = N_SIM_STUDY5
    result = {
        "meta": {
            "purpose": "Study-5 pre-registration power/feasibility; frozen "
                       "before ANY Study-5 data generation (2026-07-10).",
            "registration": "docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md",
            "master_seed": MASTER_SEED, "n_sim": N_SIM_STUDY5, "alpha": ALPHA,
            "families": ["XL H-LANG-2 (cross-language external corpus)",
                         "OS H2-3 (open-spec source diversity)",
                         "MR H2-4 (MR-side diversity)"],
            "dgp_sources": {
                "xl_hlang2_primary": "data/results/sms_track2_v7c.json "
                                     "(Study-4 C-arm, delta_C=+0.2449)",
                "xl_hlang2_sensitivity": "data/results/sms_track2_v7.json "
                                         "(Study-4 Python cross arm, "
                                         "delta=0.4445)",
                "os": "data/results/sms_track2_v4.json (v1.1 methodology "
                      "verbatim)",
                "mr": "data/results/sms_track2_v7.json + "
                      "sms_track2_v7_same.json (v7 per-PUT SMS variance)",
            },
            "numpy": np.__version__, "scipy": stats.__name__.split(".")[0],
            "no_llm_calls": True,
            "additive_note": "this study5 entry point is ADDITIVE; the "
                             "default Study-4 run and power_study4.json are "
                             "byte-unchanged.",
        },
        "d_xl_hlang2_direction_power": power_study5_hlang2(s2mod),
        "e_mr_diversity": power_study5_mr(),
        "f_os_delta_delta": power_study5_os(s2mod),
    }
    OUT5.write_text(json.dumps(result, indent=2))
    print("wrote", OUT5.relative_to(ROOT))

    d = result["d_xl_hlang2_direction_power"]
    for tag, leg in d["legs"].items():
        print("[XL %s] true delta = %s | power(delta>0) by n = %s" % (
            tag, leg["dgp_true_delta"], leg["power_delta_gt0_by_n"]))
    e = result["e_mr_diversity"]
    print("[MR] sigma_put=%.4f rho_v7=%.4f" % (
        e["per_put_mean_sms"]["arm_avg_sd_sigma_put"],
        e["per_put_mean_sms"]["between_arm_rho_v7"]))
    for rho, row in e["power"].items():
        print("     %s: se=%.4f hw=%.4f power=%s" % (
            rho, row["se_n28"], row["projected_ci95_half_width"],
            row["power_confirm_by_effect"]))
    f = result["f_os_delta_delta"]
    print("[OS] Delta-delta=0.20 power @n28 = %.4f (rho=%.3f)" % (
        f["power_dd020_at_n28"], f["calibrated_paired_rho"]))


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
            "amendment_v1_2": "2026-07-09: serving-stack + recruitment-locus change "
                              "only (pre-any-Study-4-outcome). Claude-family roles "
                              "(same-arm remainder, blinded review both arms, "
                              "H4''' recruitment stratum, C-arm remainder) served "
                              "by the session harness; non-Anthropic generators "
                              "(gpt-5.5/gemini-3.5-flash/grok-4.1) stay on the "
                              "gateway at BASELINE (rich_multiplier=1). The x4 rich "
                              "slots relocate from the two arms into a dedicated "
                              "harness recruitment stratum; pooled projection "
                              "recomputed at P(n_rich>=24)>=0.90 "
                              "(b2_h4ppp_recruitment_stratum_v1_2). No threshold, "
                              "estimand, decision rule, or seed changes.",
            "numpy": np.__version__, "scipy": stats.__name__.split(".")[0],
            "no_llm_calls": True,
        },
        "a_h2_2_cross_vendor_delta_delta": power_h2_2(s2mod),
        "b_h4ppp_rich_recruitment": recruitment_multiplier(),
        "b2_h4ppp_recruitment_stratum_v1_2": recruitment_stratum_v1_2(),
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
    b2 = result["b2_h4ppp_recruitment_stratum_v1_2"]
    print("[H4''' v1.2] additive pooling (2 arm baselines @p0=%.2f + stratum); "
          "x4 sufficient=%s; chosen stratum multiplier = x%s "
          "(expected pooled n_rich %.1f, P(>=24)=%.3f); ceiling~0.905" % (
              b2["per_put_per_arm_detect_p0"], b2["x4_sufficient"],
              b2["chosen_stratum_multiplier"], b2["chosen_expected_pooled_n_rich"],
              b2["chosen_P_ge_24"]))
    c = result["c_hlang_cross_language"]
    print("[H-LANG] v5 true delta = %s | ACHIEVED C grid n=%d %s | "
          "power(delta>0) @n7 = %.4f (a2-excl n6 = %.4f) | well-powered@0.80=%s" % (
              c["v5_calibrated_true_delta"], c["n_puts"], c["c_grid_roster"],
              c["power_delta_gt0_at_n7"], c["power_delta_gt0_at_n6_a2excluded"],
              c["well_powered_at_n7"]))


if __name__ == "__main__":
    # ADDITIVE dispatcher (Study-5 registration): `--study5` runs ONLY the
    # Study-5 extension (writes power_study5.json); the default invocation is
    # the frozen Study-4 run, byte-unchanged (writes power_study4.json).
    if "--study5" in sys.argv[1:]:
        main_study5()
    else:
        main()
