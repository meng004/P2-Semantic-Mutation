#!/usr/bin/env python3
"""H-ZERO frozen analysis (headline; derivation: COR-ZERO via A-PROV).

Input JSON schema:
  {"units": [{"cell": str, "condition": "ALN"|"CRS",
              "predicted_nonzero": bool, "observed_sms": float}]}
Units = applicable cell x condition; NOT_APPLICABLE cells never enter.
Predictions are the frozen theory labels: ALN -> nonzero, CRS -> zero
(PRED_ZERO_ALIGN); the input carries them explicitly so the script stays
label-agnostic.

Criterion (frozen): observed balanced accuracy >= 0.75 AND one-sided exact
McNemar vs the majority-class predictor p < 0.05. Majority-class predictor:
assigns every unit the majority observed class on the same evaluation set
(tie -> zero). Mandatory reporting: TPR/TNR decomposition + bootstrap 95%
CI on BA (10^4, percentile over units).

Usage: analysis_hzero.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _stats import mcnemar_onesided, record  # noqa: E402

ALPHA = 0.05
BA_THRESHOLD = 0.75
UNDERPOWERED_MIN_CELLS = 40


def analyse(data: dict) -> dict:
    units = data["units"]
    pred_nz = np.array([u["predicted_nonzero"] for u in units], bool)
    obs_nz = np.array([u["observed_sms"] > 0 for u in units], bool)

    tpr = float(obs_nz[pred_nz].mean()) if pred_nz.any() else float("nan")
    tnr = float((~obs_nz[~pred_nz]).mean()) if (~pred_nz).any() else float("nan")
    ba = (tpr + tnr) / 2

    rng = np.random.default_rng(20260728)
    n = len(units)
    boots = []
    for _ in range(10_000):
        idx = rng.integers(0, n, n)
        p_, o_ = pred_nz[idx], obs_nz[idx]
        t = o_[p_].mean() if p_.any() else np.nan
        s = (~o_[~p_]).mean() if (~p_).any() else np.nan
        boots.append((t + s) / 2)
    boots = np.array(boots)
    ci = (float(np.nanquantile(boots, 0.025)), float(np.nanquantile(boots, 0.975)))

    maj_label = bool(obs_nz.mean() > 0.5)  # tie -> zero
    ours_correct = pred_nz == obs_nz
    maj_correct = obs_nz == maj_label
    b = int((ours_correct & ~maj_correct).sum())
    c = int((~ours_correct & maj_correct).sum())
    p = mcnemar_onesided(b, c)

    verdict = "PASS" if (ba >= BA_THRESHOLD and p < ALPHA) else "FAIL"
    n_cells = len({u["cell"] for u in units})
    flags = []
    if n_cells < UNDERPOWERED_MIN_CELLS:
        flags.append("UNDERPOWERED")

    return record(
        "H-ZERO", ba, ci, p, verdict,
        tpr=tpr, tnr=tnr, mcnemar_b=b, mcnemar_c=c,
        majority_label_nonzero=maj_label, n_units=n, n_cells=n_cells,
        flags=flags, criterion=f"BA>={BA_THRESHOLD} AND McNemar p<{ALPHA}",
    )


def smoke() -> None:
    rng = np.random.default_rng(7)
    units = []
    for i in range(51):
        units.append({"cell": f"c{i}", "condition": "ALN",
                      "predicted_nonzero": True,
                      "observed_sms": float(rng.random() < 0.9) * 0.3})
        units.append({"cell": f"c{i}", "condition": "CRS",
                      "predicted_nonzero": False,
                      "observed_sms": float(rng.random() < 0.1) * 0.2})
    out = analyse({"units": units})
    assert set(out) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out["verdict"] == "PASS", out
    assert 0.8 <= out["estimate"] <= 1.0
    print("SMOKE PASS analysis_hzero:", json.dumps(out)[:160])


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
