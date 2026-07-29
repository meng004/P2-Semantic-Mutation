#!/usr/bin/env python3
"""H-XI frozen analysis (secondary confirmatory, B-1; DEF-09 exactness defect).

Input JSON schema:
  {"kills": [{"cell": str, "mutant": str,
              "mutant_stratum": int, "mr_stratum": int}],
   "hzero_verdict": "PASS"|"FAIL"|null}
Each record = one (mutant, MR) kill event; strata are the generation-time
eff labels (mutant side) and the provenance labels (MR side) — both
ex-ante, never derived from kill outcomes.

Criterion (frozen): pooled xi = off-block kill mass / total kill mass
<= 0.10 (prior landmark) -> PASS, else FAIL; cell-cluster bootstrap 95%
CI reported (10^4). Estimability guard: total kills < 50 -> UNDERPOWERED
(interval-only, no PASS/FAIL). xi never gates H-ZERO/H-DISC (F-2).
If hzero_verdict is provided, the pre-registered H-ZERO x H-XI 2x2
adjudication sentence is emitted verbatim (hypotheses.md §6).

Usage: analysis_hxi.py INPUT.json [--out OUT.json] | --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from _stats import record  # noqa: E402

LANDMARK = 0.10
MIN_KILLS = 50

ADJUDICATION = {
    ("PASS", "PASS"): "Both the zero-structure prediction and the exactness diagnostic pass: theory and operationalisation are jointly corroborated.",
    ("PASS", "FAIL"): "The zero-structure prediction passes but block-exactness fails: the claim holds in a bounded form; attribution of aligned kills to target strata is impure and stated as such.",
    ("FAIL", "PASS"): "Block-exactness holds but the zero-structure prediction fails: the theory prediction is disconfirmed under a clean operationalisation (honest negative).",
    ("FAIL", "FAIL"): "Both fail: the operationalisation itself failed; no verdict on the theory is issued.",
}


def analyse(data: dict) -> dict:
    kills = data["kills"]
    total = len(kills)
    if total == 0:
        return record("H-XI", None, None, None, "UNDERPOWERED",
                      total_kills=0, guard=f"total kills < {MIN_KILLS}")
    off = np.array([k["mr_stratum"] != k["mutant_stratum"] for k in kills], bool)
    xi = float(off.mean())

    by_cell: dict[str, list[int]] = defaultdict(list)
    for i, k in enumerate(kills):
        by_cell[k["cell"]].append(i)
    cells = list(by_cell)
    rng = np.random.default_rng(20260728)
    boots = []
    for _ in range(10_000):
        pick = rng.integers(0, len(cells), len(cells))
        idx = np.concatenate([by_cell[cells[j]] for j in pick])
        boots.append(off[idx].mean())
    ci = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))

    if total < MIN_KILLS:
        verdict = "UNDERPOWERED"
    else:
        verdict = "PASS" if xi <= LANDMARK else "FAIL"

    extras = {
        "total_kills": total, "off_block_kills": int(off.sum()),
        "landmark": LANDMARK, "n_cells": len(cells),
        "family": "secondary-confirmatory (B-1)",
        "consumption_rule": "xi never alters H-ZERO/H-DISC verdicts (F-2)",
    }
    hz = data.get("hzero_verdict")
    if hz in ("PASS", "FAIL") and verdict in ("PASS", "FAIL"):
        extras["adjudication_2x2"] = ADJUDICATION[(hz, verdict)]
    return record("H-XI", xi, ci, None, verdict, **extras)


def smoke() -> None:
    rng = np.random.default_rng(5)
    kills = []
    for i in range(200):
        cell = f"c{i % 40}"
        ms = int(rng.integers(1, 6))
        rs = ms if rng.random() > 0.05 else int(rng.integers(1, 6))
        kills.append({"cell": cell, "mutant": f"m{i}",
                      "mutant_stratum": ms, "mr_stratum": rs})
    out = analyse({"kills": kills, "hzero_verdict": "PASS"})
    assert set(out) >= {"hypothesis", "estimate", "ci", "p", "verdict"}
    assert out["verdict"] == "PASS" and "adjudication_2x2" in out["extras"], out
    print("SMOKE PASS analysis_hxi:", out["estimate"], out["ci"])


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
