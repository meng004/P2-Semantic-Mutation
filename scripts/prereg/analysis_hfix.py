#!/usr/bin/env python3
"""H-FIX frozen analysis (secondary confirmatory, B-4; EXP-FIX intervention).

Derivation: THM-GAP actionability — adding one target-stratum aligned MR
to the cross set must move the target stratum from Gap_aln into coverage.

Input JSON schema:
  {"cells": [{"cell": str, "sms_j_before": float, "sms_j_after": float,
              "w_j": float, "gap_aln_before": float, "gap_aln_after": float}]}
Cells = the 15 pre-registered sampled cells (seed 20260728) with
Gap_aln > 0, predicted nonzero; R+ = cross ∪ {one aligned MR from the
existing MRSET-ALN}; SMS_j = per-stratum score of the target stratum.

Criterion (frozen): share of cells with SMS_j transitioning 0 -> positive;
Wilson 95% lower bound > 0.5 (with n=15 the implied pass bar is 12/15).
Ledger: gap_aln_after must equal gap_aln_before - w_j (THM-GAP algebraic
identity; computed from labels, tolerance 1e-9); max deviation reported.

Usage: analysis_hfix.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _stats import record, wilson_ci  # noqa: E402

GATE_LB = 0.5
LEDGER_TOL = 1e-9


def analyse(data: dict) -> dict:
    cells = data["cells"]
    n = len(cells)
    k = sum(1 for c in cells
            if c["sms_j_before"] == 0.0 and c["sms_j_after"] > 0.0)
    p_hat = k / n if n else float("nan")
    lo, hi = wilson_ci(k, n)
    ledger_dev = max(
        abs(c["gap_aln_after"] - (c["gap_aln_before"] - c["w_j"])) for c in cells
    ) if cells else float("nan")
    verdict = "PASS" if (n > 0 and lo > GATE_LB) else "FAIL"
    return record(
        "H-FIX", p_hat, (lo, hi), None, verdict,
        n_cells=n, n_transitioned=k,
        gap_ledger_max_deviation=float(ledger_dev),
        gap_ledger_ok=bool(ledger_dev <= LEDGER_TOL),
        family="secondary-confirmatory (B-4)",
        criterion=f"Wilson95 LB > {GATE_LB} on share of SMS_j 0->positive",
    )


def smoke() -> None:
    cells = []
    for i in range(15):
        w = 0.08
        cells.append({
            "cell": f"c{i}", "sms_j_before": 0.0,
            "sms_j_after": 0.4 if i < 13 else 0.0,
            "w_j": w, "gap_aln_before": 0.3, "gap_aln_after": 0.3 - w,
        })
    out = analyse({"cells": cells})
    assert set(out) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out["verdict"] == "PASS" and out["extras"]["gap_ledger_ok"], out
    print("SMOKE PASS analysis_hfix:", out["estimate"], out["ci"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        smoke()
        return
    out = analyse(json.loads(args.input.read_text()))
    text = json.dumps(out, indent=2)
    if args.out:
        args.out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
