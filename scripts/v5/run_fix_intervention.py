#!/usr/bin/env python3
"""EXP-FIX add-one repair intervention (Task 2.5, H-FIX, B-4).

Frozen protocol (hypotheses.md §5.4 / power_report.md §8):
  - Sample 15 cells with seed 20260728 from the eligible set
    applicable ∩ predicted-nonzero ∩ Gap_aln>0.
    Ex-ante instantiation: every applicable cell is predicted-nonzero under
    the ALN condition (A-PROV) and has Gap_aln(cross)>0 under provenance-as-
    coverage (the cross set never covers the target stratum and the cell's
    generation-time eff mass sits on that stratum, w_j = 1). Instrument-
    availability qualifier (fixed with the MR funnel, before any kill data):
    the designated replicate (set 1) must hold both the CRS MR (the cross
    set) and the ALN MR (the one aligned MR to add, drawn from the existing
    MRSET-ALN; nothing newly generated).
  - Sampling procedure: eligible cells sorted lexicographically by cell id;
    numpy default_rng(20260728).choice(n, 15, replace=False) over that order.
  - R+ = cross(set1 CRS MR) ∪ {set1 ALN MR}. Incremental execution only:
    both per-MR kill vectors already exist in kill_matrix_v5.json; no new
    AVP calls are made (the "增量" is the reuse of the committed matrix).
  - SMS_j = per-stratum score of the target stratum j = fraction of the
    cell's confirmed pool killed by stratum-j MRs in the set.
      before (cross only): no stratum-j MR in the set -> 0 by construction;
      after  (R+):        fraction killed by the added aligned MR.
  - Gap ledger from ex-ante labels: w_j = 1.0, gap_aln_before = 1.0,
    gap_aln_after = 0.0 (THM-GAP algebraic identity, deviation 0).
  - Criterion: Wilson 95% LB of share of cells with SMS_j 0 -> positive
    > 0.5 (bar 12/15). Failures reported verbatim.

Output: data/v5/fix_intervention_v5.json (SSOT key `fix_intervention_v5`)
        data/v5/analysis_inputs/hfix_input.json

Usage: PYTHONPATH=src .venv/bin/python scripts/v5/run_fix_intervention.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "data" / "v5" / "kill_matrix_v5.json"
OUT_SSOT = ROOT / "data" / "v5" / "fix_intervention_v5.json"
OUT_INPUT = ROOT / "data" / "v5" / "analysis_inputs" / "hfix_input.json"

SEED = 20260728
N_SAMPLE = 15
DESIGNATED_SET = 1  # first replicate, fixed ex-ante


def main() -> None:
    matrix = json.loads(MATRIX.read_text())
    by_cell = {c["cell"]: c for c in matrix["cells"]}

    eligible = []
    for cell_id in sorted(by_cell):
        c = by_cell[cell_id]
        aln = c["conditions"].get(f"set{DESIGNATED_SET}_ALN", {})
        crs = c["conditions"].get(f"set{DESIGNATED_SET}_CRS", {})
        if aln.get("measurable") and crs.get("measurable") and c["pool"]:
            eligible.append(cell_id)

    rng = np.random.default_rng(SEED)
    n_draw = min(N_SAMPLE, len(eligible))
    idx = rng.choice(len(eligible), n_draw, replace=False)
    sampled = [eligible[i] for i in sorted(idx)]

    cells_out = []
    for cell_id in sampled:
        c = by_cell[cell_id]
        pool_n = len(c["pool"])
        aln_kills = c["conditions"][f"set{DESIGNATED_SET}_ALN"]["kills"]
        crs_kills = c["conditions"][f"set{DESIGNATED_SET}_CRS"]["kills"]
        n_aln = sum(bool(v) for v in aln_kills.values())
        n_crs = sum(bool(v) for v in crs_kills.values())
        n_union = sum(bool(aln_kills.get(m)) or bool(crs_kills.get(m))
                      for m in c["pool"])
        cells_out.append({
            "cell": cell_id,
            "sms_j_before": 0.0,           # cross set holds no stratum-j MR
            "sms_j_after": n_aln / pool_n,  # kills by the one added aligned MR
            "w_j": 1.0,
            "gap_aln_before": 1.0,
            "gap_aln_after": 0.0,
            "extras": {
                "pool_n": pool_n,
                "added_mr": c["conditions"][f"set{DESIGNATED_SET}_ALN"]["mr_path"],
                "cross_mr": c["conditions"][f"set{DESIGNATED_SET}_CRS"]["mr_path"],
                "sms_set_cross_only": n_crs / pool_n,
                "sms_set_rplus": n_union / pool_n,
            },
        })

    ssot = {
        "protocol": {
            "seed": SEED,
            "n_sample": N_SAMPLE,
            "n_drawn": n_draw,
            "designated_set": DESIGNATED_SET,
            "eligible_definition": ("applicable ∩ predicted-nonzero ∩ Gap_aln>0; "
                                    "instrument availability on the designated set "
                                    "(both ALN and CRS measurable)"),
            "eligible_cells": eligible,
            "sampling": "sorted lexicographic order; default_rng(seed).choice(n, 15, replace=False)",
            "incremental": "reuses committed kill_matrix_v5.json vectors; no new AVP calls",
        },
        "sampled_cells": sampled,
        "cells": cells_out,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT_SSOT.write_text(json.dumps(ssot, indent=2))
    OUT_INPUT.parent.mkdir(parents=True, exist_ok=True)
    OUT_INPUT.write_text(json.dumps(
        {"cells": [{k: v for k, v in c.items() if k != "extras"}
                   for c in cells_out]}, indent=2))
    print(f"eligible={len(eligible)} sampled={n_draw}")
    for c in cells_out:
        print(f"  {c['cell']}: after={c['sms_j_after']:.3f} "
              f"(pool={c['extras']['pool_n']})")
    print(f"Wrote {OUT_SSOT} and {OUT_INPUT}")


if __name__ == "__main__":
    main()
