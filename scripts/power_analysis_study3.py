"""Study-3 pre-registration power / feasibility analysis (P2/P3 paper).

Study 3 re-registers the H4 attribution target after the H4' failure diagnosis
(docs/prereg_v2/H4_DIAGNOSIS.md; data/results/h4_leakage_diagnosis_v5.json):
the 117/117 multi-stratum leakage is REAL construct-level multi-invariant
coupling on structurally rich (surrogate/ML) PUTs, not a measurement artifact.
So a single-valued single-stratum purity threshold is the wrong model for those
families. Study 3 therefore registers:

  H4''-graded : a GRADED attribution measure over the rich PUT classes (c,d),
                scoring how concentrated a detected mutant's kill signal is on
                its DECLARED MetaPattern (NOETHER m_xxx). Threshold: mean primary
                -stratum kill share >= a POWERED lower bound over rich cells.
  H4''-strict : single-stratum purity on the CLEAN families {CE, HP, CF-with-
                screen}, with the P8-fixed all-family screen wired (CE/HP are
                0-leakage; CF leakage is stable and cheaply screenable).

Graded measure (chosen; alternatives in the registration §7b):
    per-mutant primary-stratum kill share
        s_m = 1[declared_MP in flipset(m)] / |flipset(m)|   (detected mutants)
    PUT statistic  = mean s_m over the detected mutants declared to that PUT
    rich aggregate = mean over the rich-class (c,d) PUTs
Justification: it is a per-mutant ratio in [0,1] that (i) equals 1 for a purely
attributed mutant, (ii) degrades gracefully to 1/f for an f-way co-flip, and
(iii) is 0 for a mis-declared kill; it needs no threshold on the LRCA magnitude
and reuses the frozen S5/audit flip definition byte-for-byte.

DGP: calibrated from the Study-2 v5 leakage distribution (design-from-prior-
study, disclosed). All Study-3 outcomes remain UNSEEN; only the v5 flip
distribution is used to set thresholds, exactly as Study-2 calibrated from v4.

No LLM / API calls. Pure resampling from committed SSOT.

Usage:
    PYTHONPATH=src python3 scripts/power_analysis_study3.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.stratum_filter import audit_matrix, ALL_FAMILIES  # noqa: E402
from p2.config.primary import PRIMARY_CELLS_V3  # noqa: E402

RESULTS = ROOT / "data" / "results"
V5_MATRIX = RESULTS / "sms_track2_v5.json"
DIAG = RESULTS / "h4_leakage_diagnosis_v5.json"
OUT = RESULTS / "power_study3.json"

MASTER_SEED = 20260708   # frozen: pre-registration freeze-date seed convention
N_SIM = 20000            # Monte-Carlo datasets per design point
N_BOOT = 10000           # inner bootstrap resamples for the graded lower bound
ALPHA = 0.05

RICH_CLASSES = ("c", "d")   # surrogate-regression + ML-classifier (H4_DIAGNOSIS §6)
CLEAN_FAMILIES = ("CE", "HP", "CF")  # 0-leakage + stable/screenable (H4_DIAGNOSIS §6)


# ---------------------------------------------------------------------------
# calibration from the frozen v5 leakage distribution
# ---------------------------------------------------------------------------
def calibrate_from_v5() -> dict:
    """Reconstruct per-mutant flip sets from the frozen v5 matrix (identical
    audit definition to the S5 scorer), then derive the graded per-PUT shares
    and the clean-family single-stratum purity from the committed data."""
    matrix = json.loads(V5_MATRIX.read_text())
    puts = sorted({k.split("_MP")[0] for k in matrix})
    audit = audit_matrix(matrix, puts, constrained=ALL_FAMILIES)

    per_put_share: dict[str, list[float]] = defaultdict(list)
    clean_detected: dict[str, list[int]] = defaultdict(list)  # 1 if single-stratum
    for r in audit["per_mutant"]:
        put, cat = r["put"], r["category"]
        prim = PRIMARY_CELLS_V3[put.lower()]
        fc, fl = r["flip_count"], r["flipped_invariants"]
        if fc >= 1:  # detected
            share = (1.0 if prim in fl else 0.0) / fc
            per_put_share[put].append(share)
            if cat in CLEAN_FAMILIES:
                clean_detected[cat].append(1 if fc == 1 else 0)

    # rich per-PUT mean shares (the graded DGP pool)
    rich_put_means = {p: float(np.mean(v)) for p, v in per_put_share.items()
                      if p[0].lower() in RICH_CLASSES and v}
    ab_put_means = {p: float(np.mean(v)) for p, v in per_put_share.items()
                    if p[0].lower() not in RICH_CLASSES and v}

    # clean-family purity: CF screened => admitted CF is single-stratum by
    # construction, so post-screen CF contributes single-stratum (1) only.
    clean_pool_post_screen = []
    clean_pool_pre_screen = []
    for cat in CLEAN_FAMILIES:
        for ok in clean_detected[cat]:
            clean_pool_pre_screen.append(ok)
            clean_pool_post_screen.append(1 if cat == "CF" else ok)  # CF -> screened pure

    return {
        "puts": puts,
        "n_screened_candidates_all_family": audit["n_screened_candidates"],
        "n_multistratum_flagged": audit["n_multistratum"],
        "rich_put_means": rich_put_means,
        "ab_put_means": ab_put_means,
        "clean_pre_screen": np.array(clean_pool_pre_screen),
        "clean_post_screen": np.array(clean_pool_post_screen),
        "per_family_multistratum": {
            f: sum(1 for r in audit["per_mutant"]
                   if r["category"] == f and r["flip_count"] >= 2)
            for f in ("CE", "OS", "HP", "TF", "SI", "CF")},
    }


# ---------------------------------------------------------------------------
# (a) H4''-graded power: mean rich-class primary-stratum share >= tau
# ---------------------------------------------------------------------------
def _boot_lower_pool(rng, pool, q=ALPHA, n_boot=N_BOOT):
    """Real one-sided percentile-bootstrap lower bound on the mean of the OBSERVED
    pool (anchor for the registration; B=10,000)."""
    n = len(pool)
    boot = rng.choice(pool, size=(n_boot, n), replace=True).mean(axis=1)
    return float(np.quantile(boot, q))


def power_graded(cal, n_rich_grid=(10, 12, 13, 15, 18, 20, 24),
                 thresholds=(0.10, 0.15, 0.20, 0.25, 0.30)):
    """One-sided test: confirm the rich-class mean primary-stratum share exceeds
    tau if its 95% one-sided lower confidence bound > tau. DGP: the empirical
    per-PUT rich share distribution (design-from-prior-study). The power grid
    uses the fully-vectorised normal-approx lower bound (mean - 1.645*SE), which
    for a sample mean matches the percentile bootstrap to <0.01 at these n; the
    registered analysis-time rule is the B=10,000 percentile bootstrap, whose
    lower bound on the OBSERVED pool is reported as `boot_lower_observed`."""
    rng = np.random.default_rng(MASTER_SEED + 1)
    pool = np.array(list(cal["rich_put_means"].values()), dtype=float)
    true_mean = float(pool.mean())
    z = 1.6448536269514722  # one-sided 95%

    out = {
        "measure": "per-mutant primary-stratum kill share; PUT mean; rich-class "
                   "(c,d) mean aggregate",
        "dgp_source": "data/results/sms_track2_v5.json rich-class per-PUT shares "
                      "(design-from-prior-study; Study-3 outcomes unseen)",
        "rich_put_share_pool": sorted(round(x, 4) for x in pool.tolist()),
        "true_rich_mean_dgp": round(true_mean, 4),
        "boot_lower_observed": round(_boot_lower_pool(rng, pool), 4),
        "n_rich_in_standard_28grid": sum(
            1 for p in cal["puts"] if p[0].lower() in RICH_CLASSES),
        "decision_rule": "one-sided 95% lower confidence bound on rich-class mean "
                         "> tau (analysis: B=10,000 percentile bootstrap; power "
                         "sim: normal-approx lower bound)",
        "n_sim": N_SIM, "n_boot": N_BOOT, "alpha": ALPHA,
        "power_by_threshold": {}, "min_n_rich_80pct": {},
    }
    for tau in thresholds:
        curve = {}
        for n in n_rich_grid:
            S = rng.choice(pool, size=(N_SIM, n), replace=True)
            means = S.mean(axis=1)
            ses = S.std(axis=1, ddof=1) / np.sqrt(n)
            lo = means - z * ses
            curve[n] = float((lo > tau).mean())
        out["power_by_threshold"][f"tau_{tau}"] = curve
        hit = [n for n in n_rich_grid if curve[n] >= 0.80]
        out["min_n_rich_80pct"][f"tau_{tau}"] = (min(hit) if hit else None)
    return out


# ---------------------------------------------------------------------------
# (b) H4''-strict power: single-stratum purity on the clean families
# ---------------------------------------------------------------------------
def power_strict(cal, thresholds=(0.90, 0.95),
                 true_purities=(0.97, 0.98, 0.99, 1.00)):
    """Confirm single-stratum purity >= threshold on the clean-family detected
    pool with the P8-fixed all-family screen wired. Post-screen CF is single-
    stratum by construction, so the observed v5 purity is 1.0; the test is
    powered against conservative residual screen-escape rates."""
    rng = np.random.default_rng(MASTER_SEED + 2)
    n_clean_post = int(cal["clean_post_screen"].size)
    obs_purity_post = float(cal["clean_post_screen"].mean())
    obs_purity_pre = float(cal["clean_pre_screen"].mean())

    out = {
        "measure": "fraction of DETECTED clean-family {CE,HP,CF-with-screen} "
                   "mutants that are single-stratum (flip<=1)",
        "n_clean_detected_post_screen": n_clean_post,
        "observed_purity_post_screen_v5": round(obs_purity_post, 4),
        "observed_purity_pre_screen_v5": round(obs_purity_pre, 4),
        "cf_multistratum_screened_out": int(
            cal["per_family_multistratum"]["CF"]),
        "decision_rule": "one-sided 95% lower Clopper-Pearson bound on purity "
                         ">= threshold",
        "n_sim": N_SIM, "power": {}, "min_true_purity_80pct": {},
    }
    from scipy import stats as sps

    def lower_cp(k, n, alpha=ALPHA):
        if k == n:
            return alpha ** (1.0 / n)
        return sps.beta.ppf(alpha, k, n - k + 1)

    for thr in thresholds:
        pcurve = {}
        for p in true_purities:
            rej = 0
            for _ in range(N_SIM):
                k = int(rng.binomial(n_clean_post, p))
                if lower_cp(k, n_clean_post) >= thr:
                    rej += 1
            pcurve[f"true_{p}"] = rej / N_SIM
        out["power"][f"threshold_{thr}"] = pcurve
        hit = [p for p in true_purities if pcurve[f"true_{p}"] >= 0.80]
        out["min_true_purity_80pct"][f"threshold_{thr}"] = (min(hit) if hit else None)
    return out


# ---------------------------------------------------------------------------
# (c) registered smoke assertion basis: the all-family screen must match >0
# ---------------------------------------------------------------------------
def screen_smoke(cal) -> dict:
    return {
        "all_family_screen_matched_candidates": int(
            cal["n_screened_candidates_all_family"]),
        "must_be_gt_zero": True,
        "multistratum_flagged_all_family": int(cal["n_multistratum_flagged"]),
        "per_family_multistratum_v5": cal["per_family_multistratum"],
        "note": "The Study-3 campaign registers a smoke assertion that the wired "
                "all-family screen matches >0 candidates and (on a re-audit of "
                "any leakage-bearing family) flags >0 double-flips. A screen that "
                "matches zero candidates is the incident-P8 silent no-op and MUST "
                "fail the campaign loudly.",
    }


def main():
    cal = calibrate_from_v5()
    print("calibration: rich per-PUT shares n=%d true_mean=%.4f | clean n=%d "
          "purity_post=%.3f | all-family screen matched=%d flagged=%d" % (
              len(cal["rich_put_means"]),
              float(np.mean(list(cal["rich_put_means"].values()))),
              cal["clean_post_screen"].size, cal["clean_post_screen"].mean(),
              cal["n_screened_candidates_all_family"],
              cal["n_multistratum_flagged"]))

    result = {
        "meta": {
            "purpose": "Study-3 pre-registration power/feasibility; frozen before "
                       "any Study-3 data generation.",
            "master_seed": MASTER_SEED, "n_sim": N_SIM, "n_boot": N_BOOT,
            "alpha": ALPHA,
            "graded_dgp_source": "data/results/sms_track2_v5.json (rich-class "
                                 "per-PUT primary-stratum shares; design-from-"
                                 "prior-study, Study-3 outcomes unseen)",
            "diagnosis_ref": "docs/prereg_v2/H4_DIAGNOSIS.md; "
                             "data/results/h4_leakage_diagnosis_v5.json",
            "numpy": np.__version__,
            "rich_classes": list(RICH_CLASSES),
            "clean_families": list(CLEAN_FAMILIES),
        },
        "a_h4pp_graded_power": power_graded(cal),
        "b_h4pp_strict_power": power_strict(cal),
        "c_screen_smoke_assertion": screen_smoke(cal),
        "ab_class_descriptive": {
            "note": "a/b classes are NOT in the graded target (they are near-pure "
                    "or classical); reported descriptively.",
            "ab_put_share_mean": round(
                float(np.mean(list(cal["ab_put_means"].values()))), 4),
        },
    }
    OUT.write_text(json.dumps(result, indent=2))
    print("wrote", OUT.relative_to(ROOT))

    g = result["a_h4pp_graded_power"]
    print("\n(a) H4''-graded true rich mean =", g["true_rich_mean_dgp"],
          "| n_rich in standard 28-grid =", g["n_rich_in_standard_28grid"])
    for tau, curve in g["power_by_threshold"].items():
        print("   ", tau, {k: round(v, 2) for k, v in curve.items()},
              "min_n_rich80 =", g["min_n_rich_80pct"][tau])
    s = result["b_h4pp_strict_power"]
    print("(b) H4''-strict n_clean =", s["n_clean_detected_post_screen"],
          "obs_purity_post =", s["observed_purity_post_screen_v5"])
    for thr, curve in s["power"].items():
        print("   ", thr, curve)
    print("(c) all-family screen matched =",
          result["c_screen_smoke_assertion"]["all_family_screen_matched_candidates"],
          "flagged =",
          result["c_screen_smoke_assertion"]["multistratum_flagged_all_family"])


if __name__ == "__main__":
    main()
