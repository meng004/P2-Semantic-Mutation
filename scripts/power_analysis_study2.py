"""Study-2 pre-registration power analysis (P2/P3 semantic-mutation paper).

REAL Monte-Carlo power simulations that fix the Study-1 power lessons flagged in
docs/review_2026-07-08/r3_statistics.md (focus 3/4) and r1_methodology.md
(focus 1/4). Every registered threshold in
docs/prereg_v2/PREREGISTRATION_STUDY2.md must trace to the JSON this script
writes to data/results/power_study2.json.

Three power questions (see r3_statistics.md):
  (a) Cliff's delta two-sample power (aligned j=k vs cross j!=k) at
      n_PUT in {12,18,24,30,36}, DGP calibrated to the Study-1 v4 MP5-held pool
      (the pool that generates the headline delta=0.314, zero-inflated SMS).
      -> minimum n for >=80% power at the registered confirmatory threshold.
  (b) Dual-blind source-diversity Delta-delta detection at Delta-delta in
      {0.10,0.15,0.20} as a function of n_PUT; justifies the registered n.
  (c) Industrial expansion: exact Wilcoxon / sign-flip power at
      n_cases in {34,45,52} for the T1>B1 paired contrast, calibrated to the
      Study-1 per-case effect distribution; plus Fisher detection-incidence power.

No LLM / API calls. Pure resampling from committed SSOT.

Usage:
    PYTHONPATH=src python3 scripts/power_analysis_study2.py
    (system python3 has numpy>=2 / scipy>=1.17; repo .venv is not materialised)
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data" / "results"
OUT = RESULTS / "power_study2.json"

MASTER_SEED = 20260708  # frozen: pre-registration freeze date
N_SIM = 2000            # Monte-Carlo datasets per (design point)
N_BOOT = 400            # inner bootstrap resamples for delta CI
ALPHA = 0.05


# ---------------------------------------------------------------------------
# DGP calibration from Study-1 v4 SSOT (sms_track2_v4.json, MP5-held convention)
# ---------------------------------------------------------------------------
def load_study1_sms_hurdle() -> dict:
    """Reconstruct the aligned (j=k) / cross (j!=k) SMS arrays from the v4 pool
    under the pre-registered MP5-held primary convention (src/p2/config/primary.py
    PRIMARY_CELLS_V3). This is the pool that generates the headline delta=0.314;
    it is the honest, conservative Study-1 effect (r3 M2)."""
    sms = json.loads((RESULTS / "sms_track2_v4.json").read_text())
    prim = {"a": 1, "b": 2, "c": 5, "d": 2}  # PRIMARY_CELLS_V3, per class
    puts = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3", "d1", "d2", "d3"]
    aligned, cross = [], []
    for p in puts:
        cls = p[0]
        for mp in range(1, 6):
            key = f"{p.upper()}_MP{mp}"
            if key not in sms:
                continue
            v = sms[key]["sms"]
            (aligned if mp == prim[cls] else cross).append(float(v))
    aligned = np.array(aligned)
    cross = np.array(cross)
    return {
        "aligned": aligned,
        "cross": cross,
        "aligned_nonzero_mag": aligned[aligned > 0],
        "cross_nonzero_mag": cross[cross > 0],
        "p_nonzero_aligned": float((aligned > 0).mean()),
        "p_nonzero_cross": float((cross > 0).mean()),
        "mean_aligned": float(aligned.mean()),
        "mean_cross": float(cross.mean()),
    }


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """delta = P(a>b) - P(a<b), sign-based, ties count 0."""
    diff = np.sign(a[:, None] - b[None, :])
    return float(diff.mean())


def sample_hurdle(rng: np.random.Generator, n: int, p_nz: float, mags: np.ndarray) -> np.ndarray:
    """Draw n zero-inflated SMS values: with prob p_nz draw a nonzero magnitude
    (bootstrapped from the observed nonzero pool), else 0."""
    nz = rng.random(n) < p_nz
    out = np.zeros(n)
    k = int(nz.sum())
    if k:
        out[nz] = rng.choice(mags, size=k, replace=True)
    return out


def delta_boot_ci_lower(rng, a, b, n_boot=N_BOOT, q=0.05):
    """One-sided (lower) percentile-bootstrap bound on Cliff's delta via the
    exact multinomial-weight two-sample bootstrap: delta* = (wr @ D @ wc)/(na*nc)
    where wr,wc are multinomial(n, uniform) resample-count vectors. This equals
    the standard nonparametric two-sample bootstrap and is BLAS-vectorised."""
    na, nc = len(a), len(b)
    D = np.sign(a[:, None] - b[None, :])  # na x nc in {-1,0,1}
    WR = rng.multinomial(na, np.full(na, 1.0 / na), size=n_boot).astype(float)  # (B,na)
    WC = rng.multinomial(nc, np.full(nc, 1.0 / nc), size=n_boot).astype(float)  # (B,nc)
    tmp = WC @ D.T                       # (B, na)
    deltas = np.einsum("bi,bi->b", WR, tmp) / (na * nc)
    return float(np.quantile(deltas, q)), float(D.mean())


# ---------------------------------------------------------------------------
# (a) Cliff's delta two-sample power for the aligned-vs-cross contrast
# ---------------------------------------------------------------------------
def power_cliffs(dgp, n_puts=(12, 18, 24, 30, 36), thresholds=(0.0, 0.147, 0.330)):
    """Design: each PUT contributes 1 aligned diagonal cell + 4 cross cells.
    n_aligned = n_PUT, n_cross = 4*n_PUT. Decision rule (registered test):
    reject H0: delta<=delta_ref one-sided if the 95% one-sided lower bootstrap
    bound on Cliff's delta exceeds delta_ref (alpha=0.05)."""
    rng = np.random.default_rng(MASTER_SEED + 1)
    out = {"design": "n_aligned=n_PUT, n_cross=4*n_PUT; one-sided 95% bootstrap "
                     "lower bound on Cliff's delta > delta_ref",
           "dgp": {k: (v if np.isscalar(v) else np.asarray(v).round(4).tolist())
                   for k, v in dgp.items() if k in
                   ("p_nonzero_aligned", "p_nonzero_cross", "mean_aligned",
                    "mean_cross", "aligned_nonzero_mag", "cross_nonzero_mag")},
           "true_delta_dgp": None,
           "n_sim": N_SIM, "n_boot": N_BOOT,
           "power_by_threshold": {}, "min_n_80pct": {}}
    # empirical "true" delta of the DGP (large-sample)
    big_a = sample_hurdle(rng, 60000, dgp["p_nonzero_aligned"], dgp["aligned_nonzero_mag"])
    big_c = sample_hurdle(rng, 240000, dgp["p_nonzero_cross"], dgp["cross_nonzero_mag"])
    out["true_delta_dgp"] = round(cliffs_delta(big_a[:4000], big_c[:16000]), 4)
    for thr in thresholds:
        curve = {}
        for n in n_puts:
            na, nc = n, 4 * n
            rej = 0
            for _ in range(N_SIM):
                a = sample_hurdle(rng, na, dgp["p_nonzero_aligned"], dgp["aligned_nonzero_mag"])
                c = sample_hurdle(rng, nc, dgp["p_nonzero_cross"], dgp["cross_nonzero_mag"])
                lo, _d = delta_boot_ci_lower(rng, a, c)
                if lo > thr:
                    rej += 1
            curve[n] = rej / N_SIM
        out["power_by_threshold"][f"delta_ref_{thr}"] = curve
        hit = [n for n in n_puts if curve[n] >= 0.80]
        out["min_n_80pct"][f"delta_ref_{thr}"] = (min(hit) if hit else None)
    return out


# ---------------------------------------------------------------------------
# (b) Dual-blind source-diversity Delta-delta detection
# ---------------------------------------------------------------------------
def power_delta_delta(dgp, n_puts=(12, 18, 24, 30, 36),
                      delta_deltas=(0.10, 0.15, 0.20)):
    """Source-diversity contrast Delta-delta = delta(cross-source) - delta(same-source),
    estimated on the SAME PUTs (paired-role bootstrap, v3 vs v4 share the 12-PUT grid).

    Step 1 (REAL MC): estimate the per-arm sampling SD of delta-hat from the
    calibrated hurdle DGP at each n.
    Step 2: form SE(Delta-delta, n). v3 and v4 are paired on PUTs, so the two
    delta-hats are positively correlated; we calibrate a single paired-correlation
    rho so that SE(Delta-delta, n=12) matches the Study-1 paired-role bootstrap
    SE = 0.113 (r3_statistics.md focus 3; CI [-0.238,0.207] => SE=(0.207+0.238)/(2*1.96)).
    Step 3: MC power for a two-sided test of Delta-delta != 0 at alpha=0.05."""
    rng = np.random.default_rng(MASTER_SEED + 2)
    target_se_12 = round((0.207 + 0.238) / (2 * 1.96), 4)  # 0.1135

    per_arm_sd = {}
    for n in n_puts:
        na, nc = n, 4 * n
        ds = np.empty(600)
        for i in range(600):
            a = sample_hurdle(rng, na, dgp["p_nonzero_aligned"], dgp["aligned_nonzero_mag"])
            c = sample_hurdle(rng, nc, dgp["p_nonzero_cross"], dgp["cross_nonzero_mag"])
            ds[i] = cliffs_delta(a, c)
        per_arm_sd[n] = float(ds.std(ddof=1))

    # independent-arms SE(Delta) = sqrt(2)*sd_arm; paired reduces by sqrt(1-rho).
    # Calibrate rho so paired SE at n=12 == target_se_12.
    se_indep_12 = np.sqrt(2) * per_arm_sd[12]
    rho = float(1 - (target_se_12 / se_indep_12) ** 2)
    rho = min(max(rho, 0.0), 0.95)

    out = {"contrast": "Delta-delta = delta(cross-source) - delta(same-source), "
                       "paired on PUTs",
           "target_paired_se_n12": target_se_12,
           "per_arm_delta_sd": {str(k): round(v, 4) for k, v in per_arm_sd.items()},
           "calibrated_paired_rho": round(rho, 4),
           "paired_se_by_n": {}, "power": {}, "min_n_80pct": {}}

    se_by_n = {}
    for n in n_puts:
        se = np.sqrt(2) * per_arm_sd[n] * np.sqrt(1 - rho)
        se_by_n[n] = float(se)
    out["paired_se_by_n"] = {str(k): round(v, 4) for k, v in se_by_n.items()}

    zcrit = stats.norm.ppf(1 - ALPHA / 2)
    for dd in delta_deltas:
        curve = {}
        for n in n_puts:
            se = se_by_n[n]
            # MC: draw Delta-delta-hat ~ Normal(dd, se^2); reject if |z|>zcrit
            draws = rng.normal(dd, se, size=40000)
            z = draws / se
            curve[n] = float((np.abs(z) > zcrit).mean())
        out["power"][f"dd_{dd}"] = curve
        hit = [n for n in n_puts if curve[n] >= 0.80]
        out["min_n_80pct"][f"dd_{dd}"] = (min(hit) if hit else None)
    return out


# ---------------------------------------------------------------------------
# (c) Industrial expansion: Wilcoxon / sign-flip + Fisher incidence
# ---------------------------------------------------------------------------
def load_industrial():
    d = json.loads((RESULTS / "industrial_percase_v1.json").read_text())
    diffs, t1_face, b1_face = [], [], []
    for c in d["cases"].values():
        na = c["n_applied"]
        diffs.append(c["kills"]["T1"] / na - c["kills"]["B1"] / na)
        t1_face.append(1 if c["face"].get("t1") == "DETECT" else 0)
        b1_face.append(1 if c["face"].get("b1") else 0)
    return (np.array(diffs), np.array(t1_face), np.array(b1_face))


def power_industrial(n_cases_grid=(34, 35, 40, 45, 52)):
    diffs, t1_face, b1_face = load_industrial()
    # observed anchor
    w_obs = stats.wilcoxon(diffs, alternative="greater", zero_method="wilcox")
    out = {"study1_observed": {
                "n_cases": int(len(diffs)),
                "mean_paired_diff_T1_minus_B1": round(float(diffs.mean()), 4),
                "n_pos": int((diffs > 0).sum()), "n_neg": int((diffs < 0).sum()),
                "n_tie": int((diffs == 0).sum()),
                "wilcoxon_stat": round(float(w_obs.statistic), 3),
                "wilcoxon_p_onesided_greater": round(float(w_obs.pvalue), 4),
                "t1_face_detect": int(t1_face.sum()),
                "b1_face_detect": int(b1_face.sum())},
           "wilcoxon_power": {}, "signflip_power": {}, "fisher_incidence_power": {},
           "min_n_80pct": {}}
    rng = np.random.default_rng(MASTER_SEED + 3)
    nz = diffs[diffs != 0]  # for sign-flip test on nonzero diffs
    face_pairs = np.column_stack([t1_face, b1_face])
    for n in n_cases_grid:
        w_rej = sf_rej = fis_rej = 0
        for _ in range(N_SIM):
            samp = rng.choice(diffs, size=n, replace=True)
            # exact one-sided Wilcoxon signed-rank
            try:
                p = stats.wilcoxon(samp, alternative="greater", zero_method="wilcox").pvalue
            except ValueError:
                p = 1.0
            if p < ALPHA:
                w_rej += 1
            # sign-flip permutation test on the mean of nonzero diffs (exact MC)
            s = samp[samp != 0]
            if len(s):
                obs_mean = s.mean()
                signs = rng.choice([-1.0, 1.0], size=(1000, len(s)))
                null = (signs * np.abs(s)).mean(axis=1)
                p_sf = (1 + (null >= obs_mean).sum()) / (1 + len(null))
                if p_sf < ALPHA:
                    sf_rej += 1
            # Fisher detection-incidence (T1 vs B1 incidence)
            fp = face_pairs[rng.integers(0, len(face_pairs), size=n)]
            tab = [[int(fp[:, 0].sum()), n - int(fp[:, 0].sum())],
                   [int(fp[:, 1].sum()), n - int(fp[:, 1].sum())]]
            _, pf = stats.fisher_exact(tab, alternative="greater")
            if pf < ALPHA:
                fis_rej += 1
        out["wilcoxon_power"][n] = w_rej / N_SIM
        out["signflip_power"][n] = sf_rej / N_SIM
        out["fisher_incidence_power"][n] = fis_rej / N_SIM
    for key in ("wilcoxon_power", "signflip_power", "fisher_incidence_power"):
        hit = [n for n in n_cases_grid if out[key][n] >= 0.80]
        out["min_n_80pct"][key] = (min(hit) if hit else None)
    return out


def main():
    dgp = load_study1_sms_hurdle()
    print("DGP: mean_aligned=%.4f mean_cross=%.4f p_nz_a=%.3f p_nz_c=%.3f"
          % (dgp["mean_aligned"], dgp["mean_cross"],
             dgp["p_nonzero_aligned"], dgp["p_nonzero_cross"]))
    result = {
        "meta": {
            "purpose": "Study-2 pre-registration power analysis; frozen before "
                       "any Study-2 data generation.",
            "master_seed": MASTER_SEED, "n_sim": N_SIM, "n_boot": N_BOOT,
            "alpha": ALPHA,
            "dgp_source": "data/results/sms_track2_v4.json (MP5-held, delta=0.314 pool)",
            "industrial_source": "data/results/industrial_percase_v1.json",
            "numpy": np.__version__, "scipy": stats.__name__.split(".")[0],
        },
        "a_cliffs_delta_power": power_cliffs(dgp),
        "b_dual_blind_delta_delta": power_delta_delta(dgp),
        "c_industrial_expansion": power_industrial(),
    }
    OUT.write_text(json.dumps(result, indent=2))
    print("wrote", OUT.relative_to(ROOT))
    # console summary
    a = result["a_cliffs_delta_power"]
    print("\n(a) true DGP delta =", a["true_delta_dgp"])
    for thr, curve in a["power_by_threshold"].items():
        print("   ", thr, {k: round(v, 2) for k, v in curve.items()},
              "min_n80 =", a["min_n_80pct"][thr])
    b = result["b_dual_blind_delta_delta"]
    print("(b) paired rho =", b["calibrated_paired_rho"], "SE_by_n =", b["paired_se_by_n"])
    for dd, curve in b["power"].items():
        print("   ", dd, {k: round(v, 2) for k, v in curve.items()},
              "min_n80 =", b["min_n_80pct"][dd])
    c = result["c_industrial_expansion"]
    print("(c) obs Wilcoxon p =", c["study1_observed"]["wilcoxon_p_onesided_greater"])
    print("    wilcoxon_power   =", {k: round(v, 2) for k, v in c["wilcoxon_power"].items()})
    print("    signflip_power   =", {k: round(v, 2) for k, v in c["signflip_power"].items()})
    print("    fisher_incidence =", {k: round(v, 2) for k, v in c["fisher_incidence_power"].items()})


if __name__ == "__main__":
    main()
