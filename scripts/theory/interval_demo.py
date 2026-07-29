#!/usr/bin/env python3
"""THM-INT interval demonstration on the v4 legacy ledger (development-only).

Reads the v4 Track-2 mp-cell ledger (12 PUT x 5 MP = 60 cells) and emits, per
cell and pooled, the THM-INT interval [SMS_cons, SMS_strict] together with the
width identity SMS_strict * u / (n + u).

Caliber (Task T1.2, theory-enhancement plan):
  n = killed + survive   (every denominator member failed E1 or E2, i.e.
                          carries a divergence witness: CONFIRMED_NON_EQUIVALENT)
  k = killed
  u = equiv              (the v4 pipeline judges equivalence by single-shot
                          E1^E2 sampling only -- src/p2/equiv/judge.py; there is
                          no AST/certificate layer, so every `equiv` verdict is
                          sample-only and reads as EQUIVALENCE_UNRESOLVED under
                          DEF-01)

The output is a NEW artefact keyed `mp_cells`; no existing SSOT key is touched.
Role: development-only illustration for the future manuscript section
introducing THM-INT. It must not feed any confirmatory analysis.
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "data" / "results" / "sms_track2_v4.json"
DIAGNOSIS = REPO_ROOT / "data" / "results" / "equiv_diagnosis.json"
OUTPUT = REPO_ROOT / "data" / "results" / "interval_demo_v4.json"

U_RULE = (
    "u = cell `equiv` count: the v4 equivalence judgement is single-shot "
    "E1^E2 on K_eq=1000 samples with epsilon_eq=epsilon_AVP=1e-6 and no "
    "AST/certificate layer, so every equiv verdict is sample-only, i.e. "
    "EQUIVALENCE_UNRESOLVED under DEF-01 (see equiv_diagnosis.json, case B)."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(n: int, k: int, u: int) -> dict:
    """THM-INT quantities for one accounting unit (requires n >= 1)."""
    sms_strict = k / n
    sms_cons = k / (n + u)
    width = sms_strict * u / (n + u)
    return {
        "n": n,
        "k": k,
        "u": u,
        "sms_strict": sms_strict,
        "sms_cons": sms_cons,
        "width": width,
    }


def main() -> int:
    ledger = json.loads(LEDGER.read_text())

    mp_cells: dict[str, dict] = {}
    for cell in sorted(ledger):
        rec = ledger[cell]
        k = rec["killed"]
        survive = rec["survive"]
        equiv = rec["equiv"]
        inst = rec["inst"]
        if inst != k + survive + equiv:
            print(
                f"ledger integrity violation in {cell}: "
                f"inst={inst} != killed+survive+equiv={k + survive + equiv}",
                file=sys.stderr,
            )
            return 1
        n = k + survive
        u = equiv
        if n < 1:
            # Manuscript denominator guard: no interval for an empty cell.
            mp_cells[cell] = {"n": n, "k": k, "u": u, "sms_strict": None,
                              "sms_cons": None, "width": None,
                              "note": "n=0, interval undefined"}
            continue
        cell_out = interval(n, k, u)
        legacy = rec.get("sms")  # stored rounded to 4 decimals in the ledger
        if legacy is not None and abs(round(cell_out["sms_strict"], 4) - legacy) > 1e-9:
            print(
                f"legacy SMS mismatch in {cell}: "
                f"strict={cell_out['sms_strict']} ledger={legacy}",
                file=sys.stderr,
            )
            return 1
        cell_out["legacy_sms"] = legacy
        mp_cells[cell] = cell_out

    defined = [c for c in mp_cells.values() if c["sms_strict"] is not None]
    widths = [c["width"] for c in defined]
    pooled = interval(
        n=sum(c["n"] for c in defined),
        k=sum(c["k"] for c in defined),
        u=sum(c["u"] for c in defined),
    )

    out = {
        "schema": "interval_demo_v1",
        "provenance": {
            "role": "development-only (THM-INT illustration; not confirmatory)",
            "generated_by": "scripts/theory/interval_demo.py",
            "ledger": {"path": str(LEDGER.relative_to(REPO_ROOT)),
                       "sha256": sha256(LEDGER)},
            "equiv_semantics_evidence": {
                "path": str(DIAGNOSIS.relative_to(REPO_ROOT)),
                "sha256": sha256(DIAGNOSIS),
            },
            "u_rule": U_RULE,
            "cell_caliber": "mp-cell (12 PUT x 5 MP, v4 legacy partition, F-8)",
        },
        "overall_pooled": pooled,
        "width_distribution": {
            "cells": len(defined),
            "nonzero_widths": sum(1 for w in widths if w > 0),
            "min": min(widths),
            "median": statistics.median(widths),
            "max": max(widths),
        },
        "mp_cells": mp_cells,
    }

    OUTPUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    print(
        f"cells={len(mp_cells)} pooled_interval="
        f"[{pooled['sms_cons']:.6f}, {pooled['sms_strict']:.6f}] "
        f"pooled_width={pooled['width']:.6f} "
        f"nonzero_width_cells={out['width_distribution']['nonzero_widths']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
