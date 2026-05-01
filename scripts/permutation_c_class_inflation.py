"""P0-4 (R0 W2 / R1 W5 / DA-CRITICAL-3): permutation null for the
c-class primary MP shift.

Question: §3.5.1 selects, for each c-class PUT (c1/c2/c3), the MP
with maximum mean SMS over MP1..MP5. This is a max-over-5 statistic.
What is the percentile rank of the observed v3b mean (c-class
aligned mean SMS) under a permutation null where MP labels within each
c-class PUT are randomly permuted?

Method:
- Read sms_track2_v4.json filtered to c-class PUTs (15 cells).
- For each of N_PERM=10000 permutations, randomly shuffle MP labels
  within each c-class PUT, recompute "selected primary MP = argmax over
  5", record the resulting c-class aligned mean SMS.
- Report: observed v3b c-class aligned mean, percentile rank in null
  distribution, Bonferroni x 5 effective alpha bound.

Output: data/results/c_class_permutation_v4.json
Run: SMS_VERSION=v4 PYTHONPATH=src .venv/bin/python scripts/permutation_c_class_inflation.py
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
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "42"))
SMS_FILE = f"sms_track2_{VERSION}.json"
OUT_FILE = f"c_class_permutation_{VERSION}.json"

print(f"permutation_c_class: SMS_VERSION={VERSION} N_PERM={N_PERM}")

sms = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

c_puts = ["c1", "c2", "c3"]
mp_indices = [1, 2, 3, 4, 5]
sms_by_put_mp = {}
for cell, v in sms.items():
    put = cell.split("_")[0].lower()
    if put not in c_puts:
        continue
    mp = int(cell.split("MP")[1])
    sms_by_put_mp.setdefault(put, {})[mp] = v["sms"]

assert all(len(sms_by_put_mp[p]) == 5 for p in c_puts), \
    f"Need 5 MPs per c-class PUT; got {[(p, len(sms_by_put_mp[p])) for p in c_puts]}"

# Observed: max-over-5 mean per c-class PUT (this is the v3b selection rule)
observed_per_put = [max(sms_by_put_mp[p].values()) for p in c_puts]
observed_c_aligned_mean = float(np.mean(observed_per_put))

# Null: shuffle MP indices within each c-class PUT, take max-over-5,
# average across the three PUTs
rng = np.random.default_rng(SEED)
null_means = np.empty(N_PERM)
for i in range(N_PERM):
    null_per_put = []
    for p in c_puts:
        vals = list(sms_by_put_mp[p].values())
        rng.shuffle(vals)
        null_per_put.append(max(vals))
    null_means[i] = float(np.mean(null_per_put))

percentile = float(np.mean(null_means >= observed_c_aligned_mean))

# Bonferroni: family of 5 MP candidates per PUT, alpha_effective = alpha / 5
alpha_naive = 0.05
alpha_bonf = alpha_naive / 5

report = {
    "version": VERSION,
    "n_perm": N_PERM,
    "seed": SEED,
    "method": "max-over-5 MP selection per c-class PUT, permute MP labels within PUT",
    "observed": {
        "per_put_max_sms": {p: float(max(sms_by_put_mp[p].values())) for p in c_puts},
        "c_class_aligned_mean": observed_c_aligned_mean,
    },
    "null_distribution": {
        "mean": float(null_means.mean()),
        "std": float(null_means.std(ddof=1)),
        "p25": float(np.percentile(null_means, 25)),
        "p50": float(np.percentile(null_means, 50)),
        "p75": float(np.percentile(null_means, 75)),
        "p95": float(np.percentile(null_means, 95)),
        "p99": float(np.percentile(null_means, 99)),
    },
    "permutation_p_value_one_sided_geq": percentile,
    "bonferroni": {
        "family_size": 5,
        "alpha_naive": alpha_naive,
        "alpha_effective": alpha_bonf,
    },
    "interpretation": (
        "permutation_p_value_one_sided_geq quantifies how often the "
        "max-over-5 rule (used in §3.5.1) achieves a c-class aligned "
        "mean SMS at least as large as observed when MP labels are "
        "exchangeable within each c-class PUT. Bonferroni-effective "
        "alpha is the conservative bound when no permutation is run. "
        "Both are sensitivity analyses for the c-class primary MP "
        "shift's selection-on-response inflation."
    ),
}

(ROOT / "data/results" / OUT_FILE).write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"observed c-class aligned mean: {observed_c_aligned_mean:.4f}")
print(f"permutation p (one-sided ≥): {percentile:.4f}")
print(f"Bonferroni effective alpha: {alpha_bonf:.4f}")
print(f"-> {OUT_FILE}")
