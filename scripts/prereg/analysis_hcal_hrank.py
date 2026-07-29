#!/usr/bin/env python3
"""H-CAL (headline, interval-estimation primary) + H-CAL-CLU (secondary B-3)
+ H-RANK (headline) frozen analysis, plus the Cohen-kappa gate utility.

Ruling chain for the H-CAL primary form (documented, pre-registered before
any external data collection): master plan Task 1.2 Step 2b delegates the
"threshold test or interval estimation" ruling to the feasibility
simulation; power_report §6.1 shows the majority-class McNemar test is
infeasible at n<=24 (max power 0.31 at acc 0.8 / 0.66 at acc 0.9);
prereg_prereview §4 passed the anti-over-defence audit; author continuation
2026-07-28. The falsifiable confirmatory element of the calibration family
is H-CAL-CLU (B-3).

Input JSON schema:
  {"cal_pairs":      [{"defect": str, "predicted_detect": bool,
                       "observed_detect": bool}],          # aligned, 1/defect
   "cal_all":        [{"defect": str, "condition": "ALN"|"V5"|"CRS"|"RND",
                       "predicted_detect": bool, "observed_detect": bool}],
   "fixed_arm_flags":[{"defect": str, "condition": str, "flagged": bool}],
   "rank_projects":  [{"project": str, "n_ready": int,
                       "predicted_rank": [int x4],   # ALN,V5,CRS,RND
                       "detected_counts": [int x4]}],
   "ms_tau_by_project":  {project: float} | null,    # classic-MS baseline
   "pc_tau_by_project":  {project: float} | null}    # pattern-coverage baseline

Frozen criteria:
  H-CAL     primary = INTERVAL_REPORTED: aligned accuracy + Wilson 95% CI;
            majority-class rate + one-sided exact McNemar reported as
            labelled descriptives (never a verdict source); Brier deleted
            (F-3a); fixed-arm flags -> separate FPR table (REM-FPOS
            discussion trigger), never in the primary estimand;
            n < 12 ready defects -> DESCRIPTIVE_ONLY.
  H-CAL-CLU secondary (B-3): pooled 4-condition accuracy vs majority-class
            predictor, defect-cluster bootstrap (10^4) one-sided p < 0.05.
  H-RANK    tau_b per qualifying project (>=3 ready defects) between the
            frozen predicted condition ranking and observed detection
            counts; tau_bar = equal-weight mean; PASS iff tau_bar >= 0.3
            AND J_qualifying >= 6; if J_qualifying < 6 -> pre-registered
            DOWNGRADED_INTERVAL (bootstrap 95% CI on tau_bar over
            projects); fully-tied projects excluded and counted.
            tau_bar_SMS - tau_bar_MS / - tau_bar_PC: paired difference +
            bootstrap 95% CI, estimation-first (no superiority test).

Usage: analysis_hcal_hrank.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from _stats import cohen_kappa, mcnemar_onesided, record, wilson_ci  # noqa: E402

ALPHA = 0.05
TAU_MID = 0.3
J_FLOOR = 6
MIN_READY = 12
N_BOOT = 10_000


def kappa_gate(labels_a: list, labels_b: list, gate: float = 0.6) -> dict:
    """Joint-label Cohen kappa gate for the blind fiber mapping (Task 3.2)."""
    k = cohen_kappa(labels_a, labels_b)
    return {"kappa": k, "gate": gate, "passes": bool(k >= gate)}


def _hcal(data: dict) -> dict:
    pairs = data["cal_pairs"]
    n = len(pairs)
    correct = np.array(
        [p["predicted_detect"] == p["observed_detect"] for p in pairs], bool
    )
    obs = np.array([p["observed_detect"] for p in pairs], bool)
    acc = float(correct.mean()) if n else float("nan")
    lo, hi = wilson_ci(int(correct.sum()), n) if n else (float("nan"),) * 2
    maj_label = bool(obs.mean() >= 0.5)
    maj_correct = obs == maj_label
    b = int((correct & ~maj_correct).sum())
    c = int((~correct & maj_correct).sum())
    p_desc = mcnemar_onesided(b, c)
    flags = data.get("fixed_arm_flags", [])
    n_flag = sum(1 for f in flags if f["flagged"])
    fpr = n_flag / len(flags) if flags else None
    verdict = "DESCRIPTIVE_ONLY" if n < MIN_READY else "INTERVAL_REPORTED"
    return record(
        "H-CAL", acc, (lo, hi), None, verdict,
        n_defects=n, majority_rate=float(maj_correct.mean()) if n else None,
        mcnemar_descriptive_p=p_desc, mcnemar_b=b, mcnemar_c=c,
        fixed_arm_fpr=fpr, fixed_arm_n=len(flags),
        primary_form="interval estimation (pre-registered ruling chain in docstring)",
        brier="deleted (F-3a)",
    )


def _hcal_clu(data: dict) -> dict:
    rows = data["cal_all"]
    defects = sorted({r["defect"] for r in rows})
    by_defect = {d: [r for r in rows if r["defect"] == d] for d in defects}
    obs_all = np.array([r["observed_detect"] for r in rows], bool)
    maj_label = bool(obs_all.mean() >= 0.5)

    def acc_diff(defect_sample: list[str]) -> float:
        ours = maj = tot = 0
        for d in defect_sample:
            for r in by_defect[d]:
                tot += 1
                ours += r["predicted_detect"] == r["observed_detect"]
                maj += r["observed_detect"] == maj_label
        return (ours - maj) / tot if tot else 0.0

    theta = acc_diff(defects)
    rng = np.random.default_rng(20260728)
    boots = np.array([
        acc_diff([defects[i] for i in rng.integers(0, len(defects), len(defects))])
        for _ in range(N_BOOT)
    ])
    p = float((1 + (boots <= 0).sum()) / (1 + N_BOOT))
    ci = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))
    return record(
        "H-CAL-CLU", theta, ci, p, "PASS" if p < ALPHA else "FAIL",
        n_defect_clusters=len(defects), n_rows=len(rows),
        family="secondary-confirmatory (B-3)",
        criterion="cluster-bootstrap one-sided p<0.05 for (accuracy - majority) > 0",
    )


def _hrank(data: dict) -> list[dict]:
    projects = data["rank_projects"]
    taus, tied, skipped = [], 0, 0
    for pr in projects:
        if pr["n_ready"] < 3:
            skipped += 1
            continue
        counts = pr["detected_counts"]
        if len(set(counts)) == 1:
            tied += 1
            continue
        tau, _ = stats.kendalltau(pr["predicted_rank"], counts)
        if np.isfinite(tau):
            taus.append(float(tau))
    j_q = len(taus) + tied
    tau_bar = float(np.mean(taus)) if taus else float("nan")
    rng = np.random.default_rng(20260728)
    if taus:
        arr = np.array(taus)
        boots = np.array([
            arr[rng.integers(0, len(arr), len(arr))].mean() for _ in range(N_BOOT)
        ])
        ci = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))
    else:
        ci = (float("nan"), float("nan"))
    if j_q < J_FLOOR:
        verdict = "DOWNGRADED_INTERVAL"
    else:
        verdict = "PASS" if tau_bar >= TAU_MID else "FAIL"
    out = [record(
        "H-RANK", tau_bar, ci, None, verdict,
        J_qualifying=j_q, J_skipped_lt3=skipped, J_fully_tied=tied,
        taus=taus, criterion=f"tau_bar>={TAU_MID} with J_qualifying>={J_FLOOR}",
    )]
    for name, key in (("MS", "ms_tau_by_project"), ("PC", "pc_tau_by_project")):
        base = data.get(key)
        if not base:
            continue
        common = [pr["project"] for pr in projects
                  if pr["n_ready"] >= 3 and pr["project"] in base
                  and len(set(pr["detected_counts"])) > 1]
        pairs = []
        for pr in projects:
            if pr["project"] in common:
                tau, _ = stats.kendalltau(pr["predicted_rank"], pr["detected_counts"])
                pairs.append(float(tau) - float(base[pr["project"]]))
        if not pairs:
            continue
        arr = np.array(pairs)
        boots = np.array([
            arr[rng.integers(0, len(arr), len(arr))].mean() for _ in range(N_BOOT)
        ])
        ci_d = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))
        out.append(record(
            f"H-RANK-diff-vs-{name}", float(arr.mean()), ci_d, None,
            "ESTIMATE_REPORTED",
            n_projects=len(arr),
            note="estimation-first; no superiority test at J~8 (B-3 rationale)",
        ))
    return out


def analyse(data: dict) -> list[dict]:
    return [_hcal(data), _hcal_clu(data)] + _hrank(data)


def smoke() -> None:
    rng = np.random.default_rng(9)
    pairs = [{"defect": f"d{i}", "predicted_detect": True,
              "observed_detect": bool(rng.random() < 0.85)} for i in range(20)]
    cal_all = []
    for i in range(24):
        for cond, pd_, po in (("ALN", True, 0.9), ("V5", True, 0.75),
                              ("CRS", False, 0.3), ("RND", False, 0.1)):
            cal_all.append({"defect": f"d{i}", "condition": cond,
                            "predicted_detect": pd_,
                            "observed_detect": bool(rng.random() < po)})
    projects = []
    for j in range(8):
        counts = [int(rng.binomial(3, p)) for p in (0.9, 0.65, 0.4, 0.1)]
        projects.append({"project": f"p{j}", "n_ready": 3,
                         "predicted_rank": [4, 3, 2, 1],
                         "detected_counts": counts})
    data = {"cal_pairs": pairs, "cal_all": cal_all,
            "fixed_arm_flags": [{"defect": f"d{i}", "condition": "ALN",
                                 "flagged": bool(rng.random() < 0.05)}
                                for i in range(20)],
            "rank_projects": projects,
            "ms_tau_by_project": {f"p{j}": 0.2 for j in range(8)},
            "pc_tau_by_project": None}
    out = analyse(data)
    names = [o["hypothesis"] for o in out]
    assert names[:3] == ["H-CAL", "H-CAL-CLU", "H-RANK"], names
    for o in out:
        assert set(o) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out[0]["verdict"] == "INTERVAL_REPORTED"
    assert out[1]["verdict"] == "PASS", out[1]
    assert out[2]["verdict"] == "PASS", out[2]
    kg = kappa_gate(["DIRECT-CE"] * 8 + ["ADJACENT"] * 2,
                    ["DIRECT-CE"] * 8 + ["ADJACENT"] * 2)
    assert kg["passes"] and kg["kappa"] == 1.0
    print("SMOKE PASS analysis_hcal_hrank:",
          [f"{o['hypothesis']}={o['verdict']}" for o in out])


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
