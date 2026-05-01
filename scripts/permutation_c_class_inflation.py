"""P0-4 (R0 W2 / R1 W5 / DA-CRITICAL-3): permutation null for the
c-class primary MP shift — corrected version (cross-cell shuffle).

The selection rule §3.5.1 uses is: per c-class PUT, pick the MP with
maximum mean SMS over MP1..MP5 ("max-over-5"), then average across
the 3 c-class PUTs. The selection-inflation question is: how much of
the observed value exceeds what would arise under chance?

Method (corrected from earlier within-PUT shuffle, which was invariant
under max):
- Treat all 15 c-class cells (3 PUTs × 5 MPs) as exchangeable.
- For each permutation: shuffle the 15 SMS values, reassign to the 15
  (PUT, MP) slots in shuffled order, recompute max-over-5 per PUT,
  then average across PUTs.
- Compare observed to the null distribution.

This destroys the (PUT, MP) → SMS association so the only remaining
signal in the statistic is what the max-over-5 selection adds beyond
chance — exactly the inflation we want to bound.

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

# Observed: max-over-5 mean per c-class PUT
observed_per_put = [max(sms_by_put_mp[p].values()) for p in c_puts]
observed_c_aligned_mean = float(np.mean(observed_per_put))

# Flatten all 15 (PUT, MP) cells into one pool of SMS values
flat_values = np.array(
    [sms_by_put_mp[p][m] for p in c_puts for m in mp_indices],
    dtype=float,
)
assert len(flat_values) == 15

# Null: shuffle the 15 values across all (PUT, MP) slots (full
# exchangeability), recompute max-over-5 per PUT, average across PUTs
rng = np.random.default_rng(SEED)
null_means = np.empty(N_PERM)
for i in range(N_PERM):
    perm = rng.permutation(flat_values)
    # First 5 -> c1, next 5 -> c2, next 5 -> c3
    chunks = perm.reshape(3, 5)
    null_means[i] = float(np.mean(chunks.max(axis=1)))

percentile = float(np.mean(null_means >= observed_c_aligned_mean))

# Bonferroni: family of 5 MP candidates per PUT, alpha_effective = alpha / 5
alpha_naive = 0.05
alpha_bonf = alpha_naive / 5

report = {
    "version": VERSION,
    "n_perm": N_PERM,
    "seed": SEED,
    "method": (
        "Cross-cell exchangeability null: all 15 c-class (PUT, MP) "
        "cells are pooled, the SMS values are shuffled and reassigned, "
        "then max-over-5 per PUT is recomputed and averaged across PUTs. "
        "Earlier within-PUT shuffle was invariant under max and "
        "produced a degenerate null; this corrected version breaks the "
        "(PUT, MP) -> SMS association so the resulting null isolates "
        "the inflation introduced by max-over-5 selection beyond chance."
    ),
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
        "permutation_p_value_one_sided_geq is the fraction of "
        "permutations whose max-over-5 c-class aligned mean meets or "
        "exceeds the observed value. Low p (< 0.05) indicates the "
        "observed selection captured real MP-specific signal beyond "
        "chance; high p indicates the observed is consistent with "
        "selection inflation under exchangeability. Bonferroni "
        "effective alpha is the conservative parametric bound when "
        "no permutation is run."
    ),
}

(ROOT / "data/results" / OUT_FILE).write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"observed c-class aligned mean: {observed_c_aligned_mean:.4f}")
print(f"null mean: {null_means.mean():.4f} (std {null_means.std(ddof=1):.4f})")
print(f"permutation p (one-sided ≥): {percentile:.4f}")
print(f"Bonferroni effective alpha: {alpha_bonf:.4f}")
print(f"-> {OUT_FILE}")
