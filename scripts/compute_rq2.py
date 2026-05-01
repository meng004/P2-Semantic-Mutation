"""Compute RQ2 H2 evidence from Track-2 v2: aligned vs cross SMS.

Reads data/results/sms_track2_v2.json (60 cells), splits each cell's SMS
into aligned (k == primary MP for the PUT) vs cross (k != primary MP),
and writes Cliff's delta + 95% bootstrap CI + median odds-ratio plus
H2 pass/fail flags to data/results/rq2_cliffs_delta.json.
"""
import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS as PRIMARY  # type: ignore[import-not-found]
from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta, odds_ratio

VERSION = os.environ.get("SMS_VERSION", "v3")
SMS_FILE = f"sms_track2_{VERSION}.json" if VERSION != "v2" else "sms_track2_v2.json"
OUT_FILE = f"rq2_cliffs_delta_{VERSION}.json" if VERSION != "v2" else "rq2_cliffs_delta.json"
print(f"compute_rq2: SMS_VERSION={VERSION} reading {SMS_FILE} writing {OUT_FILE}")

data = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    target = aligned if mp_k == PRIMARY[put_id] else cross
    target.append(v["sms"])

N_BOOT = int(os.environ.get("RQ2_N_BOOT", "10000"))
delta = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=N_BOOT, alpha=0.05, seed=42)
ratio = odds_ratio(aligned, cross)

report = {
    "n_boot": N_BOOT,
    "n_aligned": len(aligned),
    "n_cross": len(cross),
    "mean_aligned": sum(aligned) / len(aligned),
    "mean_cross": sum(cross) / len(cross),
    "median_aligned": float(np.median(aligned)),
    "median_cross": float(np.median(cross)),
    "cliffs_delta": delta,
    "delta_ci_95": [lo, hi],
    "odds_ratio_median": ratio,
    "h2_threshold_delta": 0.474,
    "h2_threshold_ratio": 3.0,
    "h2_delta_pass": delta >= 0.474,
    "h2_ratio_pass": ratio >= 3.0,
}

out = ROOT / "data/results" / OUT_FILE
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
