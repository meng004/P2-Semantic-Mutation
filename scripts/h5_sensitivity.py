"""H5 threshold sensitivity analysis (R-14).

R-14 reviewer concern: is the H5 cutoff suspect_share <= 0.20 a "lucky
pick"? This script sweeps the cutoff over a dense grid and reports
h5_pass_ratio at each value, plus the underlying suspect_share
distribution percentiles.

No LRCA recomputation — operates entirely on the already-committed
lrca_60cell_{VERSION}.json output.

Output: data/results/h5_sensitivity_{VERSION}.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

VERSION = os.environ.get("SMS_VERSION", "v4")
LRCA_FILE = (
    f"lrca_60cell_{VERSION}.json"
    if VERSION not in ("v2",)
    else "lrca_60cell.json"
)
OUT_FILE = f"h5_sensitivity_{VERSION}.json"

print(f"h5_sensitivity: SMS_VERSION={VERSION} reading {LRCA_FILE}")

lrca = json.loads((ROOT / "data/results" / LRCA_FILE).read_text())
suspects = np.array([cell["suspect_share"] for cell in lrca.values()])
n = len(suspects)
print(f"  n_cells={n}, mean_suspect={suspects.mean():.4f}, "
      f"median_suspect={float(np.median(suspects)):.4f}")

# Dense grid of H5 cutoffs
cutoffs = [round(x, 2) for x in np.arange(0.05, 0.55, 0.05)]
sensitivity = []
for cut in cutoffs:
    n_pass = int((suspects <= cut).sum())
    sensitivity.append({
        "cutoff": cut,
        "h5_cells_pass": n_pass,
        "h5_pass_ratio": round(n_pass / n, 4),
    })
    print(f"  cut={cut:.2f}: pass={n_pass}/{n} ({n_pass/n:.2%})")

# Quantile profile of the suspect distribution
percentiles = [5, 10, 25, 50, 75, 90, 95]
quantiles = {f"p{p}": round(float(np.percentile(suspects, p)), 4) for p in percentiles}

# What cutoff would give H5 pass at the §5.2 80% target?
# Find the smallest cut s.t. h5_pass_ratio >= 0.80
target_80pct_cutoff = None
for s in sensitivity:
    if s["h5_pass_ratio"] >= 0.80:
        target_80pct_cutoff = s["cutoff"]
        break

# Pivot: at the paper's 0.20 cutoff, what is the answer?
paper_cutoff = 0.20
paper_pass = next((s for s in sensitivity if s["cutoff"] == paper_cutoff), None)

report = {
    "version": VERSION,
    "n_cells": n,
    "suspect_distribution": {
        "mean": round(float(suspects.mean()), 4),
        "std": round(float(suspects.std(ddof=1)), 4),
        "min": round(float(suspects.min()), 4),
        "max": round(float(suspects.max()), 4),
        "quantiles": quantiles,
    },
    "paper_h5_cutoff": paper_cutoff,
    "paper_h5_result": paper_pass,
    "sensitivity_curve": sensitivity,
    "smallest_cutoff_for_80pct_pass": target_80pct_cutoff,
    "interpretation": (
        "H5 verdict robustness: if the cutoff in {0.05..0.50} produces "
        "pass_ratio < 0.80 at any reasonable cut (e.g. 0.20-0.35), the "
        "0.20 specific value is NOT load-bearing — the H5 'unmet' verdict "
        "is robust across the cutoff family. "
        "smallest_cutoff_for_80pct_pass tells you how lenient the threshold "
        "would have to become before H5 flips to 'met'."
    ),
}

(ROOT / "data/results" / OUT_FILE).write_text(
    json.dumps(report, indent=2, ensure_ascii=False)
)
print(f"\nsmallest cutoff for 0.80 pass-ratio: {target_80pct_cutoff}")
print(f"-> {OUT_FILE}")
