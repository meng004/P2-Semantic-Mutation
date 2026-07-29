"""Post-hoc H4 cutoff sensitivity under the zero-kill-is-NA convention."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
VERSION = os.environ.get("SMS_VERSION", "v4")
LRCA_FILE = (
    f"lrca_60cell_{VERSION}.json"
    if VERSION not in ("v2",)
    else "lrca_60cell.json"
)
OUT_FILE = f"h5_sensitivity_{VERSION}.json"  # legacy filename, H4 content

print(f"h5_sensitivity: SMS_VERSION={VERSION} reading {LRCA_FILE}")
lrca = json.loads((ROOT / "data/results" / LRCA_FILE).read_text())
evaluable = [
    cell for cell in lrca.values() if int(cell["n_killed"]) > 0
]
suspects = np.array([cell["suspect_share"] for cell in evaluable], dtype=float)
n_total = len(lrca)
n_evaluable = len(evaluable)

cutoffs = [round(x, 2) for x in np.arange(0.05, 0.55, 0.05)]
sensitivity = []
for cut in cutoffs:
    n_le_cutoff = int((suspects <= cut).sum())
    sensitivity.append(
        {
            "cutoff": cut,
            "h4_evaluable_cells_le_cutoff": n_le_cutoff,
            "h4_evaluable_ratio_le_cutoff": round(
                n_le_cutoff / n_evaluable, 4
            ),
        }
    )

percentiles = [5, 10, 25, 50, 75, 90, 95]
quantiles = {
    f"p{p}": round(float(np.percentile(suspects, p)), 4)
    for p in percentiles
}

report = {
    "version": VERSION,
    "hypothesis": "H4",
    "legacy_filename_note": (
        "The h5 filename is retained for compatibility; the manuscript "
        "hypothesis is H4."
    ),
    "aggregation": "evaluable-cell macro sensitivity; zero-kill cells are NA",
    "cells_total": n_total,
    "cells_evaluable": n_evaluable,
    "cells_zero_kill_NA": n_total - n_evaluable,
    "suspect_distribution_evaluable_cells": {
        "mean": round(float(suspects.mean()), 4),
        "std": round(float(suspects.std(ddof=1)), 4),
        "min": round(float(suspects.min()), 4),
        "max": round(float(suspects.max()), 4),
        "quantiles": quantiles,
    },
    "paper_cutoff": 0.20,
    "sensitivity_curve": sensitivity,
    "interpretation": (
        "Post-hoc sensitivity only. The pre-registered all-60-cell "
        "macro estimand is undefined because zero-kill cells have "
        "suspect_share = NA; no H4 verdict is produced."
    ),
}

(ROOT / "data/results" / OUT_FILE).write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n"
)
print(
    f"  evaluable={n_evaluable}/{n_total}, "
    f"macro suspect={suspects.mean():.4f}"
)
print(f"-> {OUT_FILE}")
