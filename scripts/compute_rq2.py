"""Compute RQ2 H2 evidence from Track-2 v2: aligned vs cross SMS.

Reads data/results/sms_track2_v2.json (60 cells), splits each cell's SMS
into aligned (k == primary MP for the PUT) vs cross (k != primary MP),
and writes Cliff's delta + 95% bootstrap CI + median odds-ratio plus
H2 pass/fail flags to data/results/rq2_cliffs_delta.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta, odds_ratio

PRIMARY = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

data = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())

aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    target = aligned if mp_k == PRIMARY[put_id] else cross
    target.append(v["sms"])

delta = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=1000, alpha=0.05, seed=42)
ratio = odds_ratio(aligned, cross)

report = {
    "n_aligned": len(aligned),
    "n_cross": len(cross),
    "mean_aligned": sum(aligned) / len(aligned),
    "mean_cross": sum(cross) / len(cross),
    "median_aligned": float(sorted(aligned)[len(aligned) // 2]),
    "median_cross": float(sorted(cross)[len(cross) // 2]),
    "cliffs_delta": delta,
    "delta_ci_95": [lo, hi],
    "odds_ratio_median": ratio,
    "h2_threshold_delta": 0.474,
    "h2_threshold_ratio": 3.0,
    "h2_delta_pass": delta >= 0.474,
    "h2_ratio_pass": ratio >= 3.0,
}

out = ROOT / "data/results/rq2_cliffs_delta.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
