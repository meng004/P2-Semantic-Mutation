#!/usr/bin/env python3
"""H-DOSE (headline) + H-DOSE-CTR (secondary B-2) frozen analysis.

Derivation: THM-WIN (monotone kill transition centred near eps_tol,
width O(Delta_r + 2*eta_bar)); dose axis = REALIZED violation magnitude
eps_m (F-10: measured by the direct invariant-violation functional,
never by the MR checkers).

Input JSON schema:
  {"curves": [{"curve_id": str, "eps_realized": [float...],
               "kills": [int...], "reps": int, "eps_tol": float,
               "window_halfwidth": float|null}]}
window_halfwidth = Delta_r + 2*eta_bar per curve, estimated per the
THM-WIN audit item (5) protocol and FROZEN BEFORE dose unblinding.

H-DOSE criterion (frozen): global pooled statistic T_glob = sum over
curves of T_c (T_c = RSS_const - RSS_iso on level kill-rates); null =
within-curve permutation conditional on per-curve totals (multivariate
hypergeometric), 10^4 draws; one-sided p < 0.05. Per-curve permutation
p-values and Page's L are reported descriptively.

H-DOSE-CTR criterion (frozen): per-curve transition centre (isotonic
0.5-crossing on the realized axis; logistic-MLE crossing as sensitivity)
contained in [eps_tol - w, eps_tol + w]; PASS iff >= 6 of 8 curves
contained; NOT_EVALUABLE if any window_halfwidth is missing.

Usage: analysis_hdose.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _stats import dose_T, page_L, pava_means, record  # noqa: E402

ALPHA = 0.05
N_PERM = 10_000
CTR_MIN_CONTAINED = 6


def _centre_isotonic(eps: np.ndarray, kills: np.ndarray, reps: int) -> float | None:
    fit = pava_means(kills.astype(float), np.full(len(kills), float(reps)))
    above = np.nonzero(fit >= 0.5)[0]
    if len(above) == 0:
        return None
    i = above[0]
    if i == 0:
        return float(eps[0])
    f0, f1 = fit[i - 1], fit[i]
    frac = (0.5 - f0) / (f1 - f0) if f1 > f0 else 0.5
    return float(eps[i - 1] + frac * (eps[i] - eps[i - 1]))


def analyse(data: dict) -> list[dict]:
    curves = data["curves"]
    rng = np.random.default_rng(20260728)

    t_obs_per, null_draws = [], []
    for cv in curves:
        kills = np.asarray(cv["kills"], int)
        reps, L = int(cv["reps"]), len(cv["kills"])
        t_obs_per.append(dose_T(kills, reps))
        k_tot = int(kills.sum())
        draws = np.empty(N_PERM)
        for b in range(N_PERM):
            k_null = rng.multivariate_hypergeometric([reps] * L, k_tot)
            draws[b] = dose_T(np.asarray(k_null), reps)
        null_draws.append(draws)
    t_glob = float(sum(t_obs_per))
    null_glob = np.sum(null_draws, axis=0)
    p_glob = float((1 + (null_glob >= t_glob).sum()) / (1 + N_PERM))
    per_curve_p = [
        float((1 + (nd >= t).sum()) / (1 + N_PERM))
        for t, nd in zip(t_obs_per, null_draws)
    ]

    rates = np.array([np.asarray(c["kills"], float) / c["reps"] for c in curves])
    L_page, p_page = page_L(rates)

    hdose = record(
        "H-DOSE", t_glob, None, p_glob,
        "PASS" if p_glob < ALPHA else "FAIL",
        per_curve_T=[float(t) for t in t_obs_per], per_curve_p=per_curve_p,
        page_L=L_page, page_p_descriptive=p_page, n_perm=N_PERM,
        criterion=f"global within-curve permutation p<{ALPHA}",
    )

    contained, centres, missing_window = [], [], False
    for cv in curves:
        w = cv.get("window_halfwidth")
        centre = _centre_isotonic(
            np.asarray(cv["eps_realized"], float),
            np.asarray(cv["kills"], int), int(cv["reps"]),
        )
        centres.append(centre)
        if w is None:
            missing_window = True
            contained.append(None)
        else:
            contained.append(
                centre is not None and abs(centre - cv["eps_tol"]) <= w
            )
    if missing_window:
        ctr_verdict, n_cont = "NOT_EVALUABLE", None
    else:
        n_cont = int(sum(bool(c) for c in contained))
        ctr_verdict = "PASS" if n_cont >= CTR_MIN_CONTAINED else "FAIL"
    hctr = record(
        "H-DOSE-CTR", n_cont, None, None, ctr_verdict,
        centres=centres, contained=contained, family="secondary-confirmatory (B-2)",
        criterion=f">={CTR_MIN_CONTAINED}/8 curves contained in eps_tol ± (Delta_r+2*eta_bar)",
    )
    return [hdose, hctr]


def smoke() -> None:
    rng = np.random.default_rng(3)
    eps = np.exp(np.linspace(np.log(0.25), np.log(4.0), 6))
    curves = []
    for i in range(8):
        p_true = 1 / (1 + np.exp(-(eps - 1.0) / 0.1))
        curves.append({
            "curve_id": f"cv{i}", "eps_realized": [float(e) for e in eps],
            "kills": [int(rng.binomial(20, p)) for p in p_true],
            "reps": 20, "eps_tol": 1.0, "window_halfwidth": 0.4,
        })
    out = analyse({"curves": curves})
    assert out[0]["verdict"] == "PASS" and out[1]["verdict"] == "PASS", out
    for o in out:
        assert set(o) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    print("SMOKE PASS analysis_hdose:", out[0]["p"], out[1]["estimate"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        smoke()
        return
    out = analyse(json.loads(args.input.read_text()))
    text = json.dumps(out, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
