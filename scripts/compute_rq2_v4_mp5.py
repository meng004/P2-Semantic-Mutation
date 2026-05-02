"""V4 SMS data with v3 (MP5) c-class primary — strips R11 chained conditioning.

Reads sms_track2_v4.json (cross-source pool) under PRIMARY_CELLS_V3
(c1/c2/c3 → MP5), computes Cliff's delta + 95% bootstrap CI + odds ratio,
writes data/results/rq2_cliffs_delta_v4_mp5.json. This contrast feeds the
§5.3 robustness row 'v4 (under v3 MP5)' added in Task 4.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY  # explicit MP5
from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta, odds_ratio

SMS_FILE = ROOT / "data/results/sms_track2_v4.json"
OUT_FILE = ROOT / "data/results/rq2_cliffs_delta_v4_mp5.json"

data = json.loads(SMS_FILE.read_text())
aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    target = aligned if mp_k == PRIMARY[put_id] else cross
    target.append(v["sms"])

delta = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=10000, alpha=0.05, seed=42)
ratio = odds_ratio(aligned, cross)

report = {
    "design": "v4 SMS pool, c-class primary fixed at MP5 (v3 spec)",
    "purpose": "strip R11 chained conditioning by holding c-class primary at the pre-registered v3 choice",
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
    "h2_delta_pass": delta >= 0.474,
    "comparison_v3": {"delta": 0.323, "design": "v3 same-source, MP5"},
    "comparison_v4_mp1": {"delta": 0.439, "design": "v4 cross-source, MP1 (v3b post-hoc)"},
}
OUT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
