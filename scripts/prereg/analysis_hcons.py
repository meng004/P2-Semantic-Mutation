#!/usr/bin/env python3
"""H-CONS frozen analysis (manipulation check, not headline).

Input JSON schema:
  {"n_app": int, "cells": [{"cell": str, "n_confirmed_nonequiv": int}]}
`cells` lists ALL applicable cells (missing cell = 0 confirmed is not
permitted; the funnel must report every applicable cell explicitly).

Criterion (frozen): p_hat = #(cells with >=5 confirmed non-equivalent
mutants) / n_app; Wilson 95% lower bound > 0.5. Runtime-recoding
discipline is F-5a (site-absence only, pre-unblinding, logged); this
script consumes the post-F-5a cell list.

Usage: analysis_hcons.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _stats import record, wilson_ci  # noqa: E402

MIN_CONFIRMED = 5
GATE_LB = 0.5


def analyse(data: dict) -> dict:
    cells = data["cells"]
    n_app = int(data["n_app"])
    assert len(cells) == n_app, (
        f"funnel must report every applicable cell: got {len(cells)} != n_app {n_app}"
    )
    k = sum(1 for c in cells if c["n_confirmed_nonequiv"] >= MIN_CONFIRMED)
    p_hat = k / n_app
    lo, hi = wilson_ci(k, n_app)
    verdict = "PASS" if lo > GATE_LB else "FAIL"
    return record(
        "H-CONS", p_hat, (lo, hi), None, verdict,
        n_pass_cells=k, n_app=n_app, min_confirmed=MIN_CONFIRMED,
        criterion=f"Wilson95 LB > {GATE_LB} on share of cells with >= {MIN_CONFIRMED} confirmed",
        role="manipulation check (EXP-CON feasibility gate; not a headline claim)",
    )


def smoke() -> None:
    cells = [{"cell": f"c{i}", "n_confirmed_nonequiv": (16 if i < 40 else 3)}
             for i in range(51)]
    out = analyse({"n_app": 51, "cells": cells})
    assert set(out) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out["verdict"] == "PASS", out
    print("SMOKE PASS analysis_hcons:", json.dumps(out)[:160])


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
