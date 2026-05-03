"""Recompute LRCA + class-mean SMS contrasts under v4-mp5 anchoring.

Replaces v3 → v3b/v4 (MP1 c-class primary) numbers with v3 → v4-mp5
(MP5 c-class primary on both sides). Outputs:
  - mean C1_share (aligned vs cross) for v3 and v4-mp5
  - per-class mean SMS over aligned cells for v3 and v4-mp5
  - per-class shift (v3 → v4-mp5)

Anchor: PRIMARY_CELLS_V3 (c1/c2/c3 → MP5).
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}

def class_of(put_id):
    return put_id[0]  # 'a','b','c','d'

def split_aligned_cross(track2_data):
    """Returns (aligned_sms_by_class, cross_sms_by_class) lists."""
    aligned, cross = {c: [] for c in "abcd"}, {c: [] for c in "abcd"}
    for cell, v in track2_data.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        cls = class_of(put_id)
        if mp_k == PRIMARY[put_id]:
            aligned[cls].append(v["sms"])
        else:
            cross[cls].append(v["sms"])
    return aligned, cross

def lrca_c1_share_split(lrca_data):
    """Returns (aligned_c1_shares, cross_c1_shares) lists."""
    aligned, cross = [], []
    for cell, v in lrca_data.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        target = aligned if mp_k == PRIMARY[put_id] else cross
        target.append(v["c1_share"])
    return aligned, cross

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

# Load
v3_sms = json.loads((ROOT / "data/results/sms_track2_v3.json").read_text())
v4_sms = json.loads((ROOT / "data/results/sms_track2_v4.json").read_text())
v3_lrca = json.loads((ROOT / "data/results/lrca_60cell_v3.json").read_text())
v4_lrca = json.loads((ROOT / "data/results/lrca_60cell_v4.json").read_text())

# Class-mean SMS over aligned cells
v3_aligned, v3_cross = split_aligned_cross(v3_sms)
v4_aligned, v4_cross = split_aligned_cross(v4_sms)

class_means = {}
for cls in "abcd":
    v3_mean = mean(v3_aligned[cls])
    v4_mean = mean(v4_aligned[cls])
    pct_change = (v4_mean - v3_mean) / v3_mean * 100 if v3_mean > 0 else None
    class_means[cls] = {
        "v3_aligned_mean_sms": round(v3_mean, 4),
        "v4_mp5_aligned_mean_sms": round(v4_mean, 4),
        "pct_change": round(pct_change, 1) if pct_change is not None else None,
        "n_aligned_cells": len(v3_aligned[cls]),
    }

# Mean C1_share
v3_c1_aligned, v3_c1_cross = lrca_c1_share_split(v3_lrca)
v4_c1_aligned, v4_c1_cross = lrca_c1_share_split(v4_lrca)

c1_share = {
    "v3_mean_c1_share_aligned": round(mean(v3_c1_aligned), 4),
    "v3_mean_c1_share_cross": round(mean(v3_c1_cross), 4),
    "v3_mean_c1_share_overall": round(mean(v3_c1_aligned + v3_c1_cross), 4),
    "v4_mp5_mean_c1_share_aligned": round(mean(v4_c1_aligned), 4),
    "v4_mp5_mean_c1_share_cross": round(mean(v4_c1_cross), 4),
    "v4_mp5_mean_c1_share_overall": round(mean(v4_c1_aligned + v4_c1_cross), 4),
}

c1_share["pct_change_overall"] = round(
    (c1_share["v4_mp5_mean_c1_share_overall"] - c1_share["v3_mean_c1_share_overall"])
    / c1_share["v3_mean_c1_share_overall"] * 100, 1
)

# Cross-cell class means too (for completeness)
class_means_cross = {}
for cls in "abcd":
    v3_mean = mean(v3_cross[cls])
    v4_mean = mean(v4_cross[cls])
    pct_change = (v4_mean - v3_mean) / v3_mean * 100 if v3_mean > 0 else None
    class_means_cross[cls] = {
        "v3_cross_mean_sms": round(v3_mean, 4),
        "v4_mp5_cross_mean_sms": round(v4_mean, 4),
        "pct_change": round(pct_change, 1) if pct_change is not None else None,
        "n_cross_cells": len(v3_cross[cls]),
    }

# Class means over ALL 15 cells per class (primary-MP independent definition,
# matches paper Table 5 / §5.8 narrative).
def class_means_all_cells(track2_data):
    bucket = {c: [] for c in "abcd"}
    for cell, v in track2_data.items():
        bucket[cell[0].lower()].append(v["sms"])
    return {c: sum(s)/len(s) if s else 0.0 for c, s in bucket.items()}

m_v3_all = class_means_all_cells(v3_sms)
m_v4_all = class_means_all_cells(v4_sms)
class_means_all = {}
for cls in "abcd":
    pct = (m_v4_all[cls] - m_v3_all[cls]) / m_v3_all[cls] * 100 if m_v3_all[cls] > 0 else None
    class_means_all[cls] = {
        "v3_mean_sms_15cells": round(m_v3_all[cls], 4),
        "v4_mean_sms_15cells": round(m_v4_all[cls], 4),
        "pct_change": round(pct, 1) if pct is not None else None,
    }

report = {
    "design": "v3 (same-source) vs v4 (cross-source) — class-mean SMS is primary-MP-independent",
    "purpose": "Replace v3b-dagger-marked LRCA + class-mean numbers (Round-8.5)",
    "note": "Class means over all 15 cells per class do NOT depend on primary-MP choice; v4 == v4-mp5 for these averages. Original v8 † was over-cautious.",
    "anchor": "PRIMARY_CELLS_V3 (a/b/c/d → MP1/MP2/MP5/MP2)",
    "class_means_15cells": class_means_all,
    "class_means_aligned_only": class_means,
    "class_means_cross_only": class_means_cross,
    "c1_share": c1_share,
}

OUT = ROOT / "data/results/lrca_v4_mp5_recompute.json"
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
