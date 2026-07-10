#!/usr/bin/env python3
"""POST-HOC denominator sensitivity — Study-1 v4 headline under three
mutant-admission denominators (construct-validity item of the editorial review).

STATUS: POST-HOC SENSITIVITY (2026-07-10). Responds to the editorial review's
construct-validity concern: the committed Study-1 v4 headline aligned-vs-cross
Cliff's delta (rq2_cliffs_delta_v4_mp5.json, c-class primary held at MP5) uses
ALL 292 admitted mutants as the SMS denominator, of which the S5 flip audit
(s5_purity_v4.json) shows 170 are zero-flip (silent), 93 single-flip and 29
multi-flip. This script recomputes the headline contrast under three
denominators:

  1. all_admitted               all 292 admitted mutants (the committed
                                baseline; reproduced exactly as a guard);
  2. certified_declared_stratum only mutants whose flip set INCLUDES the PUT's
                                declared primary MP (PRIMARY_CELLS_V3, c->MP5);
  3. active_any_flip            only mutants with at least one flipped
                                invariant (the 93 + 29 = 122 active mutants).

WARNING — SELECTION ON THE RESPONSE. Denominators 2 and 3 condition mutant
admission on the adjudicated kill outcomes themselves (a mutant "flips" MP k
iff it is KILLED in cell PUT_MPk). Under denominator 2 every aligned cell has
SMS = 1.0 BY CONSTRUCTION. These are therefore construct-validity
sensitivities ONLY (how much of the headline contrast is carried by which
mutant stratum); they are never confirmatory and never supersede the
registered all-admitted estimand (the same reason the v3b path is prohibited).

DATA AVAILABILITY. The per-mutant flip map for v4 is FULLY derivable from the
committed SSOT data/results/sms_track2_v4.json: each of the 60 cells carries a
per-mutant outcomes list ({file, KILLED/SURVIVE}), the 5 cells of a PUT share
one mutant list, and flip(m, k) := label(m, PUT_MPk) == KILLED. The derived
map is cross-checked mutant-by-mutant against the committed flip audit
data/results/s5_purity_v4.json (292 = 170 silent + 93 pure + 29
multi-stratum); any disagreement aborts.

Both a cell-level CI (frozen multinomial two-sample method, for comparability
with the committed record) and a PUT-cluster CI (PUT-block bootstrap, the
corrected inference of compute_cluster_sensitivity.py) are reported per
denominator. B = 10,000, master seed 20260708.

Inputs (all CLOSED, read-only):
  data/results/sms_track2_v4.json           per-cell, per-mutant outcomes
  data/results/s5_purity_v4.json            committed flip audit (cross-check)
  data/results/rq2_cliffs_delta_v4_mp5.json committed headline (guard)
Output:
  data/results/denominator_sensitivity_v1.json

Usage:
    PYTHONPATH=src python3 scripts/compute_denominator_sensitivity.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "data" / "results"

MASTER_SEED = 20260708
B_BOOT = 10_000

SMS_V4 = RESULTS / "sms_track2_v4.json"
S5_PURITY = RESULTS / "s5_purity_v4.json"
COMMITTED_HEADLINE = RESULTS / "rq2_cliffs_delta_v4_mp5.json"
OUT = RESULTS / "denominator_sensitivity_v1.json"


# ---- frozen estimand machinery, imported (never re-implemented) -------------
def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DBD = _load_module("compute_dualblind_delta")
_CLUSTER = _load_module("compute_cluster_sensitivity")
cliffs_delta = _DBD.cliffs_delta
boot_delta_distribution = _DBD.boot_delta_distribution
_parse_cell = _DBD._parse_cell
PRIMARY = _DBD.PRIMARY                       # PRIMARY_CELLS_V3 (c -> MP5)
put_block_boot_delta = _CLUSTER.put_block_boot_delta


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


# --------------------------------------------------------------------------- #
# Per-mutant flip map, derived from the committed v4 SSOT
# --------------------------------------------------------------------------- #
def build_flip_map(sms: dict) -> dict:
    """{PUT: {file: sorted list of flipped MPs}} with flip := KILLED in that
    cell. Also verifies the 5 cells of a PUT share one mutant list."""
    labels: dict[str, dict[str, dict[int, str]]] = defaultdict(dict)
    for cell, v in sms.items():
        put, mp = _parse_cell(cell)
        for o in v["outcomes"]:
            labels[put].setdefault(o["file"], {})[mp] = o["label"]
    flips: dict[str, dict[str, list[int]]] = {}
    for put, files in labels.items():
        for f, per_mp in files.items():
            if sorted(per_mp) != [1, 2, 3, 4, 5]:
                raise AssertionError(
                    f"{put}/{f}: mutant not present in all 5 cells "
                    f"(has MPs {sorted(per_mp)})")
        flips[put] = {f: sorted(k for k, lab in per_mp.items()
                                if lab == "KILLED")
                      for f, per_mp in files.items()}
    return flips


def crosscheck_s5(flips: dict, s5: dict) -> dict:
    """Abort unless the derived flip map agrees mutant-by-mutant with the
    committed S5 flip audit. Returns the flip histogram summary."""
    per_mutant = s5["per_mutant"]
    derived = {(m_put, f): mps for m_put, files in flips.items()
               for f, mps in files.items()}
    if len(per_mutant) != len(derived):
        raise AssertionError(
            f"mutant count mismatch: derived {len(derived)} vs "
            f"s5_purity_v4 {len(per_mutant)}")
    n_flip = {"0": 0, "1": 0, ">=2": 0}
    for rec in per_mutant:
        key = (rec["put"].lower(), rec["file"])
        if key not in derived:
            raise AssertionError(f"s5 mutant absent from derived map: {key}")
        if derived[key] != sorted(rec["flipped_invariants"]):
            raise AssertionError(
                f"flip-set mismatch for {key}: derived {derived[key]} vs "
                f"s5 {sorted(rec['flipped_invariants'])}")
        if PRIMARY[rec["put"].lower()] != rec["primary_mp"]:
            raise AssertionError(
                f"declared-primary mismatch for {key}: PRIMARY_CELLS_V3 "
                f"{PRIMARY[rec['put'].lower()]} vs s5 {rec['primary_mp']}")
        n = len(rec["flipped_invariants"])
        n_flip["0" if n == 0 else "1" if n == 1 else ">=2"] += 1
    return {"n_admitted": len(per_mutant), "flip_histogram": n_flip,
            "expected": {"n_admitted": 292,
                         "flip_histogram": {"0": 170, "1": 93, ">=2": 29}}}


# --------------------------------------------------------------------------- #
# Denominator rules
# --------------------------------------------------------------------------- #
DENOMINATORS = {
    "all_admitted": {
        "rule": "all admitted mutants (the committed baseline denominator)",
        "include": lambda put, mps: True,
        "selection_on_response": False,
    },
    "certified_declared_stratum": {
        "rule": "flip set includes the PUT's declared primary MP "
                "(PRIMARY_CELLS_V3; aligned-cell SMS = 1.0 by construction)",
        "include": lambda put, mps: PRIMARY[put] in mps,
        "selection_on_response": True,
    },
    "active_any_flip": {
        "rule": "at least one flipped invariant (any MP killed)",
        "include": lambda put, mps: len(mps) > 0,
        "selection_on_response": True,
    },
}


def recompute_grid(sms: dict, flips: dict, include) -> tuple[dict, dict, dict]:
    """Per-cell SMS over the included mutants only.

    Returns (cell_sms, per_put_n_included, per_put_slices). Cells of a PUT
    with zero included mutants are vacant (the whole PUT drops, since the 5
    cells share one mutant list)."""
    included = {put: {f for f, mps in files.items() if include(put, mps)}
                for put, files in flips.items()}
    cell_sms: dict[str, float] = {}
    slices: dict[str, tuple[list, list]] = {}
    for cell, v in sms.items():
        put, mp = _parse_cell(cell)
        keep = included[put]
        if not keep:
            continue
        killed = sum(1 for o in v["outcomes"]
                     if o["file"] in keep and o["label"] == "KILLED")
        val = round(killed / len(keep), 4)
        cell_sms[cell] = val
        a, c = slices.setdefault(put, ([], []))
        (a if mp == PRIMARY[put] else c).append(val)
    per_put_n = {put: len(f) for put, f in included.items()}
    return cell_sms, per_put_n, slices


def analyze_denominator(name: str, spec: dict, sms: dict, flips: dict,
                        baseline_delta: float | None,
                        B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    cell_sms, per_put_n, slices = recompute_grid(sms, flips, spec["include"])
    aligned = [x for p in slices for x in slices[p][0]]
    cross = [x for p in slices for x in slices[p][1]]
    delta = round(cliffs_delta(aligned, cross), 4)
    cell_dist = boot_delta_distribution(aligned, cross, B=B, seed=seed)
    cluster_dist = put_block_boot_delta(slices, B=B, seed=seed)
    dropped = sorted(p for p, n in per_put_n.items() if n == 0)
    return {
        "rule": spec["rule"],
        "selection_on_response": spec["selection_on_response"],
        "n_mutants_included": sum(per_put_n.values()),
        "per_put_n_included": dict(sorted(per_put_n.items())),
        "puts_dropped_entirely": dropped,
        "n_cells": len(cell_sms),
        "n_aligned_cells": len(aligned),
        "n_cross_cells": len(cross),
        "mean_aligned": round(float(np.mean(aligned)), 4),
        "mean_cross": round(float(np.mean(cross)), 4),
        "cliffs_delta": delta,
        "delta_vs_all_admitted": (None if baseline_delta is None
                                  else round(delta - baseline_delta, 4)),
        "cell_level_ci": {
            "method": "frozen multinomial two-sample bootstrap "
                      "(compute_dualblind_delta.boot_delta_distribution); "
                      "reported for comparability, treats cells as independent",
            "bootstrap_B": B, "bootstrap_seed": seed,
            "one_sided_95_lower_bound": round(float(np.quantile(cell_dist, 0.05)), 4),
            "two_sided_ci95": [round(float(np.quantile(cell_dist, 0.025)), 4),
                               round(float(np.quantile(cell_dist, 0.975)), 4)],
        },
        "put_cluster_ci": {
            "method": "PUT-block bootstrap (resample PUTs with replacement, "
                      "cells travel intact) — the corrected inference",
            "bootstrap_B": B, "bootstrap_seed": seed,
            "n_puts": len(slices),
            "one_sided_95_lower_bound": round(float(np.quantile(cluster_dist, 0.05)), 4),
            "two_sided_ci95": [round(float(np.quantile(cluster_dist, 0.025)), 4),
                               round(float(np.quantile(cluster_dist, 0.975)), 4)],
        },
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(out_path=OUT, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    sms = load_json(SMS_V4)
    s5 = load_json(S5_PURITY)
    committed = load_json(COMMITTED_HEADLINE)
    flips = build_flip_map(sms)
    audit = crosscheck_s5(flips, s5)
    if audit["flip_histogram"] != audit["expected"]["flip_histogram"]:
        raise AssertionError(f"flip histogram mismatch: {audit}")

    # Guard: the all-admitted recomputation must reproduce the committed
    # per-cell SMS values and the committed headline delta exactly.
    cell_sms, _, _ = recompute_grid(sms, flips, lambda p, m: True)
    for cell, v in sms.items():
        if abs(cell_sms[cell] - float(v["sms"])) > 5e-5:
            raise AssertionError(
                f"cell {cell}: recomputed SMS {cell_sms[cell]} != committed "
                f"{v['sms']} — denominator reconstruction is wrong, aborting")

    results = {}
    baseline_delta = None
    for name, spec in DENOMINATORS.items():
        r = analyze_denominator(name, spec, sms, flips, baseline_delta,
                                B=B, seed=seed)
        if name == "all_admitted":
            baseline_delta = r["cliffs_delta"]
            if abs(r["cliffs_delta"] - round(committed["cliffs_delta"], 4)) > 5e-5:
                raise AssertionError(
                    f"all_admitted delta {r['cliffs_delta']} != committed "
                    f"headline {round(committed['cliffs_delta'], 4)}")
            r["reproduces_committed_headline"] = (
                "yes: matches rq2_cliffs_delta_v4_mp5.json::cliffs_delta "
                f"({round(committed['cliffs_delta'], 4)}); committed cell-level "
                f"CI there is {committed['delta_ci_95']} (B=10000, seed 42, "
                "p2.stats.cliffs_delta.bootstrap_delta_ci)")
        results[name] = r

    report = {
        "artefact": "denominator_sensitivity_v1",
        "generated_by": "scripts/compute_denominator_sensitivity.py",
        "status": "POST-HOC SENSITIVITY (2026-07-10): responds to the "
                  "editorial review's construct-validity item on the Study-1 "
                  "v4 SMS denominator. NOT confirmatory; the registered "
                  "all-admitted estimand stands. Denominators 2-3 condition "
                  "on the response (see selection_on_response flags) and are "
                  "reported for transparency only.",
        "inputs": {
            "sms_pool": "data/results/sms_track2_v4.json",
            "flip_audit_crosscheck": "data/results/s5_purity_v4.json",
            "committed_headline": "data/results/rq2_cliffs_delta_v4_mp5.json",
        },
        "master_seed": seed,
        "bootstrap_B": B,
        "primary_mp_rule": "PRIMARY_CELLS_V3 (c-class held at MP5, matching "
                           "the committed v4_mp5 headline; v3b prohibited)",
        "per_mutant_flip_map_availability": (
            "FULLY DERIVABLE from committed artifacts: sms_track2_v4.json "
            "carries per-mutant KILLED/SURVIVE outcomes in all 60 cells; the "
            "derived flip map agrees mutant-by-mutant with the committed S5 "
            "flip audit (s5_purity_v4.json). Nothing needed for this "
            "sensitivity is missing."),
        "flip_audit_crosscheck": audit,
        "denominators": results,
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2,
                                             ensure_ascii=False))
    return report


def _print(report: dict) -> None:
    print("=== POST-HOC denominator sensitivity (Study-1 v4, MP5 headline) ===")
    print(f"flip audit: {report['flip_audit_crosscheck']['flip_histogram']} "
          f"over n={report['flip_audit_crosscheck']['n_admitted']} (matches "
          "committed s5_purity_v4.json)")
    for name, r in report["denominators"].items():
        print(f"[{name}] n_mutants={r['n_mutants_included']} "
              f"delta={r['cliffs_delta']:+.4f} "
              f"(vs baseline {r['delta_vs_all_admitted']}) "
              f"cell CI {r['cell_level_ci']['two_sided_ci95']} | "
              f"cluster lower={r['put_cluster_ci']['one_sided_95_lower_bound']:+.4f} "
              f"CI {r['put_cluster_ci']['two_sided_ci95']} "
              f"(n_puts={r['put_cluster_ci']['n_puts']})")
        if r["puts_dropped_entirely"]:
            print(f"    PUTs dropped: {r['puts_dropped_entirely']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(OUT),
                    help="output path ('-' = stdout only)")
    args = ap.parse_args()
    out = None if args.out == "-" else args.out
    report = run(out_path=out)
    _print(report)
    if out is not None:
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
