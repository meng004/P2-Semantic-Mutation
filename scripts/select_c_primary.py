"""Find best primary MP for each class c PUT based on v3 SMS data.

For class c (c1, c2, c3): compute mean SMS per MP across 3 PUTs.
Recommend new primary = argmax_mp mean_sms(class_c, mp).

Background: §5.8.4 Friedman per-class for class c gave p = 0.406
(no significant MP difference). The original primary MP=5 for c was
inherited from P1; in absence of statistical preference, the data-driven
choice is the MP with the highest mean SMS across c1/c2/c3.
"""
import json
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent

sms = json.loads((ROOT / "data/results/sms_track2_v3.json").read_text())
c_puts = ["c1", "c2", "c3"]
per_put_mp_sms = {}
mean_per_mp = {f"MP{k}": [] for k in (1, 2, 3, 4, 5)}
for p in c_puts:
    per_put_mp_sms[p] = {}
    for mp in (1, 2, 3, 4, 5):
        cell = f"{p.upper()}_MP{mp}"
        s = sms.get(cell, {}).get("sms", 0.0)
        per_put_mp_sms[p][f"MP{mp}"] = s
        mean_per_mp[f"MP{mp}"].append(s)

mean_per_mp_avg = {k: float(np.mean(v)) for k, v in mean_per_mp.items()}
best_mp = max(mean_per_mp_avg, key=lambda k: mean_per_mp_avg[k])
report = {
    "per_put_mp_sms": per_put_mp_sms,
    "mean_per_mp_class_c": mean_per_mp_avg,
    "current_primary": "MP5",
    "new_primary_recommended": best_mp,
    "rationale": (
        "Friedman per-class p=0.406 for class c (§5.8.4) → no MP "
        "dominates statistically; data-driven choice = argmax of "
        "class-mean SMS across c1/c2/c3, avoiding fixed-by-design MP5."
    ),
}
out = ROOT / "data/results/c_class_mp_ranking.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
