#!/usr/bin/env python3
"""H-DISC frozen analysis (headline; derivation: THM-GAP decomposition).

Input JSON schema:
  {"pairs": [{"cell": str, "sms_aln": float, "sms_crs": float}]}
Pairs = applicable, predicted-nonzero cells; each SMS value is the mean
over the s=2 held-out MR-set replicates (frozen design constant).

Criterion (frozen): one-sided Wilcoxon signed-rank (aligned > cross)
p < 0.05 AND matched-pairs rank-biserial r_mp >= MID = 0.33.
Reporting: Hodges-Lehmann shift + BCa 95% CI on r_mp (10^4);
sensitivity: unpaired Cliff's delta (v4-comparable).

Usage: analysis_hdisc.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _stats import (bootstrap_ci, cliffs_delta, hodges_lehmann, record,  # noqa: E402
                    wilcoxon_greater)

ALPHA = 0.05
MID_RMP = 0.33
UNDERPOWERED_MIN_PAIRS = 30


def _rmp_stat(d: np.ndarray) -> float:
    from scipy import stats as st
    d = d[d != 0]
    if len(d) < 2:
        return 0.0
    ranks = st.rankdata(np.abs(d))
    t_pos = ranks[d > 0].sum()
    t_neg = ranks[d < 0].sum()
    return float((t_pos - t_neg) / (t_pos + t_neg))


def analyse(data: dict) -> dict:
    pairs = data["pairs"]
    aln = np.array([p["sms_aln"] for p in pairs], float)
    crs = np.array([p["sms_crs"] for p in pairs], float)
    d = aln - crs

    p, r_mp = wilcoxon_greater(d)
    ci = bootstrap_ci(d, _rmp_stat, n_boot=10_000, seed=20260728, method="bca")
    hl = hodges_lehmann(d)
    delta_unpaired = cliffs_delta(aln, crs)

    verdict = "PASS" if (p < ALPHA and r_mp >= MID_RMP) else "FAIL"
    n_nonzero = int((d != 0).sum())
    flags = ["UNDERPOWERED"] if n_nonzero < UNDERPOWERED_MIN_PAIRS else []

    return record(
        "H-DISC", r_mp, ci, p, verdict,
        hodges_lehmann_shift=float(hl), cliffs_delta_sensitivity=float(delta_unpaired),
        n_pairs=len(pairs), n_nonzero_pairs=n_nonzero, mid=MID_RMP, flags=flags,
        criterion=f"Wilcoxon(greater) p<{ALPHA} AND r_mp>={MID_RMP}",
    )


def smoke() -> None:
    rng = np.random.default_rng(11)
    pairs = []
    for i in range(51):
        a = rng.beta(0.844, 1.134) if rng.random() < 0.8 else 0.0
        c = rng.beta(2.14, 3.09) if rng.random() < 0.19 else 0.0
        pairs.append({"cell": f"c{i}", "sms_aln": round(a, 4), "sms_crs": round(c, 4)})
    out = analyse({"pairs": pairs})
    assert set(out) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out["verdict"] == "PASS", out
    print("SMOKE PASS analysis_hdisc:", json.dumps(out)[:160])


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
