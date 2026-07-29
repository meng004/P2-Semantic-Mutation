#!/usr/bin/env python3
"""Pre-registration power / feasibility simulation (argumentation-uplift Task 1.2).

Covers:
  Step 1  — two-part distribution parameters from v4 development data
            (both anchors: PUT x class-primary-MP split; operator-level
            alignment-map split).
  Step 2  — H-ZERO (balanced accuracy + McNemar) and H-DISC (paired
            Wilcoxon signed-rank + matched-pairs rank-biserial r_mp)
            power over the design grid n_app x density x MR-set count,
            plus the mandatory budget arithmetic table.
  Step 2b — external-line feasibility: H-CAL (exact McNemar vs majority
            class) and H-RANK (project-equal-weight Kendall tau_b over
            4 conditions, tie diagnostics) over n x J grids with a
            DEF-CAL-informed prevalence scan.
  Step 2c — H-DOSE isotonic-vs-constant permutation power under a
            theory-derived logistic transition family (parameters are
            NOT fitted to v4 data; slope sensitivity scan), transition-
            centre estimation precision (for the H-DOSE-CTR lock), and
            the analytic H-CONS Wilson CI width budget.

Deterministic: seeded rng(20260728). Output: data/results/prereg_power_v2.json.
Env: N_SIM (default 2000), N_SIM_DOSE (default 800), N_PERM_DOSE (default 300).
Note: the real EXP-DOSE analysis uses 10^4 permutations; the reduced count
here only affects Monte-Carlo error of the *power estimate* (~±2%).
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

RNG = np.random.default_rng(20260728)
N_SIM = int(os.environ.get("N_SIM", "2000"))
N_SIM_DOSE = int(os.environ.get("N_SIM_DOSE", "800"))
N_PERM_DOSE = int(os.environ.get("N_PERM_DOSE", "300"))
ALPHA = 0.05

ALIGN = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}


# --------------------------------------------------------------------------
# Step 1: development-data parameter extraction (two anchors)
# --------------------------------------------------------------------------
def beta_mom(x: np.ndarray) -> tuple[float, float]:
    x = np.clip(x, 1e-6, 1 - 1e-6)
    m, v = x.mean(), x.var(ddof=1)
    if v <= 0 or len(x) < 2:
        return float("nan"), float("nan")
    c = m * (1 - m) / v - 1
    return float(m * c), float((1 - m) * c)


def extract_dev_parameters() -> dict:
    from p2.config.primary import PRIMARY_CELLS_V3

    data = json.loads((ROOT / "data/results/sms_track2_v4.json").read_text())

    # Anchor A: PUT x class-primary-MP split (plan-instructed source).
    aligned, cross = [], []
    for cell, v in data.items():
        put = cell.split("_")[0].lower()
        mp = int(cell.split("MP")[1])
        (aligned if mp == PRIMARY_CELLS_V3[put] else cross).append(v["sms"])
    aligned, cross = np.array(aligned), np.array(cross)
    a_nz, c_nz = aligned[aligned > 0], cross[cross > 0]
    anchor_a = {
        "p_nonzero_aligned": float((aligned > 0).mean()),
        "p_nonzero_cross": float((cross > 0).mean()),
        "beta_aligned": beta_mom(a_nz),
        "beta_cross": beta_mom(c_nz),
        "nonzero_mean_aligned": float(a_nz.mean()),
        "nonzero_mean_cross": float(c_nz.mean()),
        "n_cells": [int(len(aligned)), int(len(cross))],
    }

    # Anchor B: operator-level alignment-map split (pessimistic; v4 MR sets
    # were class-primary-instantiated, never operator-targeted).
    import re
    from collections import defaultdict

    cellmap: dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for key, v in data.items():
        put = key.split("_")[0].lower()
        mp = int(key.split("MP")[1])
        for o in v["outcomes"]:
            m = re.match(r"m\d+_([a-d]\d)_([A-Z]+)\d+_", o["file"])
            if not m or m.group(2) not in ALIGN:
                continue
            c = cellmap[(m.group(2), put)][mp]
            c[1] += 1
            c[0] += o["label"] == "KILLED"
    aln_s, crs_s = [], []
    for (op, put), mps in cellmap.items():
        amp = ALIGN[op]
        if amp not in mps:
            continue
        a = mps[amp]
        ck = sum(x[0] for k, x in mps.items() if k != amp)
        ct = sum(x[1] for k, x in mps.items() if k != amp)
        aln_s.append(a[0] / a[1])
        if ct:
            crs_s.append(ck / ct)
    aln_s, crs_s = np.array(aln_s), np.array(crs_s)
    anchor_b = {
        "p_nonzero_aligned": float((aln_s > 0).mean()),
        "p_nonzero_cross": float((crs_s > 0).mean()),
        "beta_cross": beta_mom(crs_s[crs_s > 0]),
        "aligned_nonzero_all_ones": bool(np.all(aln_s[aln_s > 0] == 1.0)),
        "n_op_cells": int(len(aln_s)),
    }
    return {"anchor_a_put_mp_primary": anchor_a, "anchor_b_operator_level": anchor_b}


# --------------------------------------------------------------------------
# Two-part generative model
# --------------------------------------------------------------------------
def draw_two_part(n, p_nz, beta_ab, rng, degenerate_one=False):
    theta = np.zeros(n)
    nz = rng.random(n) < p_nz
    if degenerate_one:
        theta[nz] = 1.0
    else:
        theta[nz] = rng.beta(beta_ab[0], beta_ab[1], nz.sum())
    return theta


def observed_sms(theta, m, s, rng):
    """Observed SMS with density m and s MR-set replicates (mean of s draws)."""
    kills = rng.binomial(m, np.tile(theta, (s, 1)))
    return kills.mean(axis=0) / m


# --------------------------------------------------------------------------
# Step 2: H-DISC and H-ZERO
# --------------------------------------------------------------------------
def wilcoxon_rmp(d):
    """One-sided (greater) Wilcoxon signed-rank p + matched-pairs rank-biserial."""
    d = d[d != 0]
    if len(d) < 5:
        return 1.0, 0.0
    ranks = stats.rankdata(np.abs(d))
    t_pos = ranks[d > 0].sum()
    t_neg = ranks[d < 0].sum()
    r_mp = (t_pos - t_neg) / (t_pos + t_neg)
    try:
        p = stats.wilcoxon(d, alternative="greater", method="approx").pvalue
    except ValueError:
        p = 1.0
    return float(p), float(r_mp)


def mcnemar_onesided(b, c):
    """Exact one-sided McNemar: P(X >= b), X ~ Bin(b+c, 1/2)."""
    n = b + c
    if n == 0:
        return 1.0
    return float(stats.binom.sf(b - 1, n, 0.5))


def sim_hdisc_hzero(scenarios, n_apps, densities, mr_sets):
    out = []
    for scen_idx, (scen_name, sc) in enumerate(scenarios.items()):
        for n_app in n_apps:
            for m in densities:
                for s in mr_sets:
                    rng = np.random.default_rng(
                        [20260728, scen_idx, n_app, m, s]
                    )
                    hits_p = np.zeros(N_SIM, bool)
                    rmps = np.zeros(N_SIM)
                    ba = np.zeros(N_SIM)
                    zero_hits = np.zeros(N_SIM, bool)
                    for i in range(N_SIM):
                        th_a = draw_two_part(
                            n_app, sc["p_a"], sc["beta_a"], rng,
                            degenerate_one=sc.get("aligned_one", False),
                        )
                        th_c = draw_two_part(n_app, sc["p_c"], sc["beta_c"], rng)
                        obs_a = observed_sms(th_a, m, s, rng)
                        obs_c = observed_sms(th_c, m, s, rng)
                        # H-DISC
                        p, r = wilcoxon_rmp(obs_a - obs_c)
                        hits_p[i] = p < ALPHA
                        rmps[i] = r
                        # H-ZERO: aligned units predicted NONZERO, cross ZERO
                        tpr = (obs_a > 0).mean()
                        tnr = (obs_c == 0).mean()
                        ba[i] = (tpr + tnr) / 2
                        ours_correct = np.concatenate([obs_a > 0, obs_c == 0])
                        observed_nonzero = np.concatenate([obs_a > 0, obs_c > 0])
                        maj_label = observed_nonzero.mean() >= 0.5
                        maj_correct = observed_nonzero == maj_label
                        b_ = int((ours_correct & ~maj_correct).sum())
                        c_ = int((~ours_correct & maj_correct).sum())
                        zero_hits[i] = (
                            ba[i] >= 0.75 and mcnemar_onesided(b_, c_) < ALPHA
                        )
                    row = {
                        "scenario": scen_name, "n_app": n_app,
                        "density": m, "mr_sets": s,
                        "hdisc_power_p": float(hits_p.mean()),
                        "hdisc_mean_rmp": float(rmps.mean()),
                        "hdisc_q10_rmp": float(np.quantile(rmps, 0.10)),
                        "hzero_mean_ba": float(ba.mean()),
                        "hzero_power": float(zero_hits.mean()),
                    }
                    for mid in (0.30, 0.33, 0.40):
                        row[f"hdisc_power_mid{mid}"] = float(
                            (hits_p & (rmps >= mid)).mean()
                        )
                    out.append(row)
    return out


# --------------------------------------------------------------------------
# H-CONS analytic Wilson budget
# --------------------------------------------------------------------------
def wilson_bounds(p_hat, n, z=1.959963984540054):
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def hcons_budget(n_apps):
    rows = []
    for n in n_apps:
        for p_hat in np.arange(0.55, 0.96, 0.05):
            lo, hi = wilson_bounds(float(p_hat), n)
            rows.append({
                "n_app": n, "p_hat": round(float(p_hat), 2),
                "wilson_lo": round(float(lo), 4), "wilson_hi": round(float(hi), 4),
                "width": round(float(hi - lo), 4),
                "passes_gate_lb_gt_0.5": bool(lo > 0.5),
            })
    return rows


# --------------------------------------------------------------------------
# Step 2b: external line
# --------------------------------------------------------------------------
def sim_hcal(ns, prevalences, accuracies):
    out = []
    for n in ns:
        for pi in prevalences:
            for acc in accuracies:
                rng = np.random.default_rng([20260728, n, int(pi * 100), int(acc * 100)])
                hits = 0
                for _ in range(N_SIM):
                    outcome = rng.random(n) < pi          # detect / miss
                    ours_correct = rng.random(n) < acc
                    maj_pred = pi >= 0.5                   # majority predicts 'detect'
                    maj_correct = outcome == maj_pred
                    b = int((ours_correct & ~maj_correct).sum())
                    c = int((~ours_correct & maj_correct).sum())
                    hits += mcnemar_onesided(b, c) < ALPHA
                out.append({
                    "n_defects": n, "prevalence": pi, "our_accuracy": acc,
                    "power": hits / N_SIM,
                })
    return out


def sim_hrank(ns, js, scenarios):
    pred_rank = np.array([4, 3, 2, 1])  # ALN > v5 > CRS > RND predicted
    out = []
    for n in ns:
        for j in js:
            sizes = np.full(j, n // j)
            sizes[: n % j] += 1
            qual = sizes >= 3
            for scen_idx, (scen_name, probs) in enumerate(scenarios.items()):
                rng = np.random.default_rng([20260728, n, j, scen_idx])
                taus_mean, all_tied_frac = [], []
                for _ in range(N_SIM):
                    taus, tied = [], 0
                    for nj, q in zip(sizes, qual):
                        if not q:
                            continue
                        counts = rng.binomial(nj, probs)
                        if len(set(counts)) == 1:
                            tied += 1
                            continue
                        tau, _ = stats.kendalltau(pred_rank, counts)
                        if not np.isnan(tau):
                            taus.append(tau)
                    all_tied_frac.append(tied / max(qual.sum(), 1))
                    taus_mean.append(np.mean(taus) if taus else 0.0)
                taus_mean = np.array(taus_mean)
                out.append({
                    "n_defects": n, "J": j, "J_qualifying": int(qual.sum()),
                    "scenario": scen_name,
                    "mean_tau_bar": float(taus_mean.mean()),
                    "power_point_ge_0.3": float((taus_mean >= 0.3).mean()),
                    "mean_fully_tied_project_frac": float(np.mean(all_tied_frac)),
                })
    return out


# --------------------------------------------------------------------------
# Step 2c: H-DOSE
# --------------------------------------------------------------------------
def pava_means(y_sum, w):
    """Weighted isotonic (non-decreasing) fit of level means via PAVA."""
    means = y_sum / w
    blocks = [[i, means[i], w[i]] for i in range(len(means))]
    out = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][1] >= out[-1][1]:
            i0, m1, w1 = out[-2]
            _, m2, w2 = out.pop()
            out[-1] = [i0, (m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2]
    fit = np.empty(len(means))
    for k, (i0, mval, _) in enumerate(out):
        i1 = out[k + 1][0] if k + 1 < len(out) else len(means)
        fit[i0:i1] = mval
    return fit


def dose_stat(kills, reps):
    means = kills / reps
    pooled = kills.sum() / (reps * len(kills))
    rss_const = float((reps * (means - pooled) ** 2).sum())
    fit = pava_means(kills.astype(float), np.full(len(kills), float(reps)))
    rss_iso = float((reps * (means - fit) ** 2).sum())
    return rss_const - rss_iso


def sim_hdose(configs, slopes, centre=1.0):
    """Permutation null conditions on total kills K; per-level null counts are a
    multivariate hypergeometric draw (equivalent to permuting execution
    outcomes across levels). Null T-distributions are cached per (L, reps, K)."""
    grid_cache = {}
    out = []
    for (L, reps) in configs:
        if L not in grid_cache:
            grid_cache[L] = np.exp(np.linspace(np.log(0.25), np.log(4.0), L))
        eps = grid_cache[L]
        null_cache: dict[int, np.ndarray] = {}
        for s in slopes:
            p_true = 1.0 / (1.0 + np.exp(-(eps - centre) / s))
            rng = np.random.default_rng([20260728, L, reps, int(s * 1000)])
            sig = 0
            centres = []
            for _ in range(N_SIM_DOSE):
                kills = rng.binomial(reps, p_true)
                t_obs = dose_stat(kills, reps)
                k_tot = int(kills.sum())
                if k_tot not in null_cache:
                    draws = np.empty(N_PERM_DOSE)
                    for bidx in range(N_PERM_DOSE):
                        k_null = rng.multivariate_hypergeometric(
                            [reps] * L, k_tot
                        )
                        draws[bidx] = dose_stat(np.asarray(k_null), reps)
                    null_cache[k_tot] = np.sort(draws)
                t_null = null_cache[k_tot]
                p = (1 + (t_null >= t_obs).sum()) / (1 + N_PERM_DOSE)
                sig += p < ALPHA
                fit = pava_means(kills.astype(float), np.full(L, float(reps)))
                above = np.nonzero(fit >= 0.5)[0]
                if len(above) and above[0] > 0:
                    i = above[0]
                    f0, f1 = fit[i - 1], fit[i]
                    frac = (0.5 - f0) / (f1 - f0) if f1 > f0 else 0.5
                    centres.append(eps[i - 1] + frac * (eps[i] - eps[i - 1]))
                elif len(above):
                    centres.append(eps[0])
            power = sig / N_SIM_DOSE
            centres = np.array(centres)
            window = 4 * s  # ± window = Δ_r + 2η̄ ≡ 4·slope by construction
            contain = float((np.abs(centres - centre) <= window).mean()) if len(centres) else 0.0
            ge6of8 = float(1 - stats.binom.cdf(5, 8, power))
            out.append({
                "levels": L, "reps": reps, "total_executions_8curves": L * reps * 8,
                "slope_over_centre": s,
                "per_curve_power": round(power, 4),
                "power_ge6_of_8_curves": round(ge6of8, 4),
                "centre_sd": round(float(centres.std(ddof=1)), 4) if len(centres) > 1 else None,
                "centre_estimable_frac": round(len(centres) / N_SIM_DOSE, 4),
                "ctr_containment_per_curve": round(contain, 4),
                "ctr_ge6_of_8": round(float(1 - stats.binom.cdf(5, 8, contain)), 4) if contain else 0.0,
            })
    return out


# --------------------------------------------------------------------------
# Budget arithmetic
# --------------------------------------------------------------------------
def budget_table(n_apps, densities):
    rows = []
    for n in n_apps:
        for m in densities:
            total = n * m
            rows.append({
                "n_app": n, "density": m, "total_mutants": total,
                "in_master_envelope_300_840": bool(300 <= total <= 840),
                "gen_llm_calls_est": int(round(total * 1.12)),  # v4: 333 attempts / 298 confirmed
                "kill_evals_per_mrset_unit": total,
            })
    return rows


def main() -> None:
    dev = extract_dev_parameters()
    a = dev["anchor_a_put_mp_primary"]
    b = dev["anchor_b_operator_level"]

    scenarios = {
        "S_A_v4_primary_anchor": {
            "p_a": a["p_nonzero_aligned"], "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
        "S_U65_target_uplift": {
            "p_a": 0.65, "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
        "S_U80_target_uplift": {
            "p_a": 0.80, "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
        "S_ADV_operator_level": {
            "p_a": b["p_nonzero_aligned"], "beta_a": (1.0, 1.0), "aligned_one": True,
            "p_c": b["p_nonzero_cross"], "beta_c": b["beta_cross"],
        },
        # Appended after the original four so existing scenario indices
        # (and therefore their rng streams / results) stay byte-stable.
        # Purpose: localise the H-ZERO power cliff in p_a (pre-review).
        "S_U70_target_uplift": {
            "p_a": 0.70, "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
        "S_U75_target_uplift": {
            "p_a": 0.75, "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
        "S_U85_target_uplift": {
            "p_a": 0.85, "beta_a": a["beta_aligned"],
            "p_c": a["p_nonzero_cross"], "beta_c": a["beta_cross"],
        },
    }

    result = {
        "meta": {
            "seed": 20260728, "n_sim": N_SIM, "n_sim_dose": N_SIM_DOSE,
            "n_perm_dose": N_PERM_DOSE, "alpha": ALPHA,
            "generated_by": "scripts/prereg/power_simulation.py",
        },
        "step1_dev_parameters": dev,
        "step2_hdisc_hzero": sim_hdisc_hzero(
            scenarios, n_apps=[39, 45, 51], densities=[8, 12, 16, 20], mr_sets=[1, 2],
        ),
        "step2_budget": budget_table([39, 45, 51], [8, 12, 16, 20]),
        "step2c_hcons_wilson": hcons_budget([39, 45, 51]),
        "step2b_hcal": sim_hcal(
            ns=[12, 16, 20, 24],
            prevalences=[0.6, 0.7, 0.8, 0.9],
            accuracies=[0.7, 0.8, 0.9],
        ),
        "step2b_hrank": sim_hrank(
            ns=[12, 16, 20, 24], js=[6, 8, 10],
            scenarios={
                "strong": np.array([0.85, 0.65, 0.45, 0.15]),
                "moderate": np.array([0.75, 0.60, 0.45, 0.30]),
                "weak": np.array([0.65, 0.55, 0.50, 0.40]),
                # null: no condition separation; P(tau_bar >= 0.3) here is the
                # false-pass rate of the point criterion, not power.
                "null_no_separation": np.array([0.55, 0.55, 0.55, 0.55]),
            },
        ),
        "step2c_hdose": sim_hdose(
            configs=[(6, 20), (8, 15), (6, 15), (6, 10), (8, 10)],
            slopes=[0.05, 0.10, 0.20, 0.40],
        ),
    }

    out = ROOT / "data/results/prereg_power_v2.json"
    out.write_text(json.dumps(result, indent=2))
    print(f"saved -> {out}")

    print("\n== headline: H-DISC/H-ZERO power (MID=0.33, s=1) ==")
    for r in result["step2_hdisc_hzero"]:
        if r["mr_sets"] == 1 and r["n_app"] == 51:
            print(f"  {r['scenario']:24s} m={r['density']:2d} "
                  f"hdisc(p&mid.33)={r['hdisc_power_mid0.33']:.3f} "
                  f"hzero={r['hzero_power']:.3f} BA={r['hzero_mean_ba']:.3f}")


if __name__ == "__main__":
    main()
