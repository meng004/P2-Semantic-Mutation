"""RQ2 sensitivity: re-compute Cliff's δ on logit-transformed SMS.

logit(p) = log(p / (1-p)); we apply with epsilon clipping to avoid 0/1 → ±inf.
Reports δ on transformed scale + bootstrap CI.

Cliff's δ is rank-based and theoretically invariant under monotone
transformations, but with ties at 0 (most cells = 0 SMS) the logit clip
+ tie-breaking may slightly perturb δ. This is reported as a robustness
check appendix to §5.7.2, not as primary evidence.
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
from p2.stats.cliffs_delta import bootstrap_delta_ci, cliffs_delta  # type: ignore[import-not-found]

EPS = 1e-3


def logit(p: float) -> float:
    p_clipped = max(EPS, min(1 - EPS, float(p)))
    return float(np.log(p_clipped / (1 - p_clipped)))


VERSION = os.environ.get("SMS_VERSION", "v3b")
SMS_FILE = f"sms_track2_{VERSION}.json" if VERSION != "v2" else "sms_track2_v2.json"
OUT_FILE = f"rq2_cliffs_delta_logit_{VERSION}.json" if VERSION != "v2" else "rq2_cliffs_delta_logit.json"

data = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

aligned, cross = [], []
aligned_raw, cross_raw = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    s = v["sms"]
    s_logit = logit(s)
    if mp_k == PRIMARY[put_id]:
        aligned.append(s_logit)
        aligned_raw.append(s)
    else:
        cross.append(s_logit)
        cross_raw.append(s)

delta_logit = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=1000, alpha=0.05, seed=42)
delta_raw = cliffs_delta(aligned_raw, cross_raw)

report = {
    "source": SMS_FILE,
    "primary_version": os.environ.get("P2_PRIMARY_VERSION", "v3"),
    "transform": f"logit(SMS) with clip eps={EPS}",
    "n_aligned": len(aligned),
    "n_cross": len(cross),
    "mean_aligned_logit": float(np.mean(aligned)),
    "mean_cross_logit": float(np.mean(cross)),
    "cliffs_delta_logit": delta_logit,
    "delta_ci_95_logit_lo": lo,
    "delta_ci_95_logit_hi": hi,
    "cliffs_delta_raw_for_reference": delta_raw,
    "delta_raw_minus_logit": delta_raw - delta_logit,
    "transform_note": (
        "Cliff's δ is rank-based and invariant under monotone transformations "
        "in theory. With ties at 0 (76% cells = 0 SMS) the logit clip + "
        "tie-breaking perturbation should be minimal. Reported as robustness "
        "check; if |δ_raw − δ_logit| < 0.05 we declare consistency."
    ),
    "consistency_check": "PASS" if abs(delta_raw - delta_logit) < 0.05 else "FAIL",
}
out = ROOT / "data/results" / OUT_FILE
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"\nsaved -> {out}")
