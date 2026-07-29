#!/usr/bin/env python3
"""EXP-DIS kill matrices (Task 2.2 Step 2) + frozen-analysis input builder.

Ex-ante operationalisation spec (fixed BEFORE any kill execution; this
docstring is the committed record):

  Units. cell = operator × PUT over the 51 applicable cells
  (applicability_matrix.md §3). Denominator per cell = the funnel-confirmed
  non-equivalent v5 pool (data/v5/pools/, m <= 16; power_report.md §5 "kill-
  matrix denominator"). Equivalence was judged once in the Task 2.1 funnel
  (E1∧E2, v4 constants); kill matrices never re-judge it.

  Conditions. ALN(cell) = the held-out MR of stratum ALIGNED_MP[op] for the
  cell's PUT; CRS(cell) = the held-out MR of stratum CROSS_MP[op], where
  CROSS_MP is the fixed cyclic map (ALIGNED_MP[op] mod 5) + 1:
      CE(1)->2, OS(2)->3, HP(3)->4, TF(4)->5, SI(5)->1.
  Rationale (ex-ante): cardinality-matched 1-vs-1 conditions (removes the
  |R| confound from H-DISC), matches the v4 anchor estimates the power
  simulation was calibrated on (per-MP single-MR cells, power_report.md §1),
  and balances every stratum exactly once as a cross target across the five
  operators. COR-ZERO applies: Cov(CRS) ∩ {j: w_j>0} = ∅ under provenance-
  as-coverage, so CRS is predicted ZERO; ALN predicted NONZERO (A-PROV).

  Kill predicate. Per (mutant, MR): kill ⇔ AVP(S, mr) = PASS ∧
  AVP(s', mr) = FAIL, both sides by 20-repeat majority vote
  (call_avp_repeated; v4 convention "K_avp = 20", power_report.md §5),
  epsilon 1e-6. The original-side verdict is cached per (PUT, MR).
  SMS(cell, cond, set) = #kills / |pool|. Cell-condition SMS = mean over
  the s=2 set replicates where measurable.

  Measurability. A (cell, condition, set) is measurable iff the MR slot was
  won in prescreen AND AVP(S, mr) = PASS at kill time. Unmeasurable entries
  are excluded and logged — never imputed, never coerced to observed zero.
  H-ZERO unit (cell, condition) enters iff at least one set replicate is
  measurable; H-DISC pair enters iff both ALN and CRS are measurable.

  Engineering losses. Per-mutant AVP exceptions/timeouts are logged and the
  mutant counts as NOT killed for that MR (conservative, symmetric across
  conditions); completeness is reported per cell.

Outputs:
  data/v5/kill_matrix_v5.json          (full per-mutant kill booleans + spec)
  data/v5/analysis_inputs/hzero_input.json
  data/v5/analysis_inputs/hdisc_input.json
  data/v5/analysis_inputs/hxi_input.json   (kills w/ ex-ante strata labels)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/v5/run_kill_matrix.py [--workers 6]
  ... --cells CE:a1,OS:b2   (smoke subset)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import signal
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

POOLS = ROOT / "data" / "v5" / "pools"
MRS_DIR = ROOT / "data" / "v5" / "mrs"
OUT_MATRIX = ROOT / "data" / "v5" / "kill_matrix_v5.json"
OUT_INPUTS = ROOT / "data" / "v5" / "analysis_inputs"

EPSILON_AVP = 1e-6
REPEATS = 20                  # v4 convention (K_avp)
SETS = (1, 2)
MUTANT_TIMEOUT_S = 600

ALIGNED_MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}
CROSS_MP = {op: (mp % 5) + 1 for op, mp in ALIGNED_MP.items()}

APPLICABLE_CELLS: list[tuple[str, str]] = [
    ("CE", "a1"), ("CE", "a2"), ("CE", "a3"),
    ("CE", "b1"), ("CE", "b2"), ("CE", "b3"),
    ("CE", "c1"), ("CE", "c2"), ("CE", "c3"),
    ("OS", "a1"), ("OS", "a2"), ("OS", "a3"),
    ("OS", "b1"), ("OS", "b2"), ("OS", "b3"),
    ("OS", "c1"), ("OS", "c2"), ("OS", "c3"),
    ("OS", "d1"), ("OS", "d2"), ("OS", "d3"),
    ("HP", "a1"), ("HP", "a3"),
    ("HP", "b1"), ("HP", "b2"), ("HP", "b3"),
    ("HP", "c1"), ("HP", "c2"), ("HP", "c3"),
    ("HP", "d1"), ("HP", "d2"), ("HP", "d3"),
    ("TF", "a1"), ("TF", "a3"),
    ("TF", "b2"),
    ("TF", "c1"), ("TF", "c2"), ("TF", "c3"),
    ("TF", "d1"), ("TF", "d2"), ("TF", "d3"),
    ("SI", "a1"), ("SI", "a2"), ("SI", "a3"),
    ("SI", "b3"),
    ("SI", "c1"), ("SI", "c2"), ("SI", "c3"),
    ("SI", "d1"), ("SI", "d2"), ("SI", "d3"),
]
assert len(APPLICABLE_CELLS) == 51


class _Timeout(Exception):
    pass


def _alarm(signum, frame):  # noqa: ARG001
    raise _Timeout()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _compile_mr_file(path: Path, mp_k: int, name: str):
    import numpy as np
    from p2.avp.interface import MR
    code = path.read_text()
    ns: dict = {"math": math, "np": np, "numpy": np}
    exec(compile(code, str(path), "exec"), ns)  # noqa: S102
    return MR(r=ns["r"], R=ns["R"], mp_index=mp_k, name=name)


def eval_cell(op: str, put: str) -> dict:
    """Worker: full kill evaluation for one applicable cell."""
    from p2.avp.interface import AVPResult
    from p2.avp.repeat import call_avp_repeated

    cell = f"{op}×{put}"
    rec = {
        "cell": cell, "op": op, "put": put,
        "mutant_stratum": ALIGNED_MP[op],
        "aln_mp": ALIGNED_MP[op], "crs_mp": CROSS_MP[op],
        "pool": [], "conditions": {}, "sms": {}, "log": [],
    }

    pool_dir = POOLS / f"{put}_{op}"
    man_path = pool_dir / "manifest.json"
    if not man_path.exists():
        rec["log"].append("NO_POOL")
        return rec
    manifest = json.loads(man_path.read_text())
    mutants = []
    for m in manifest["mutants"]:
        mid = m["mutant_id"]
        try:
            mod = _load_module(f"mut_{put}_{op}_{mid}", pool_dir / f"{mid}.py")
            mutants.append((mid, mod.program))
        except Exception as e:  # noqa: BLE001
            rec["log"].append(f"{mid}: LOAD_FAIL {str(e)[:100]}")
    rec["pool"] = [mid for mid, _ in mutants]

    put_mod = _load_module(f"put_{put}", ROOT / f"src/p2/puts/{put}.py")
    orig_fn = put_mod.program

    for set_id in SETS:
        for cond, mp_k in (("ALN", ALIGNED_MP[op]), ("CRS", CROSS_MP[op])):
            key = f"set{set_id}_{cond}"
            mr_path = MRS_DIR / f"set{set_id}" / f"{put}_mp{mp_k}.py"
            entry = {"mr_path": str(mr_path.relative_to(ROOT)), "mp": mp_k,
                     "measurable": False, "orig_pass": None, "kills": {}}
            rec["conditions"][key] = entry
            if not mr_path.exists():
                entry["reason"] = "MR_SLOT_EMPTY"
                continue
            try:
                mr = _compile_mr_file(mr_path, mp_k, f"{put.upper()}_mp{mp_k}_s{set_id}")
            except Exception as e:  # noqa: BLE001
                entry["reason"] = f"MR_COMPILE_FAIL {str(e)[:100]}"
                continue
            signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(MUTANT_TIMEOUT_S)
            try:
                orig_pass = call_avp_repeated(orig_fn, mr, EPSILON_AVP,
                                              repeats=REPEATS) == AVPResult.PASS
            except _Timeout:
                entry["reason"] = "ORIG_AVP_TIMEOUT"
                continue
            except Exception as e:  # noqa: BLE001
                entry["reason"] = f"ORIG_AVP_ERROR {str(e)[:100]}"
                continue
            finally:
                signal.alarm(0)
            entry["orig_pass"] = orig_pass
            if not orig_pass:
                entry["reason"] = "ORIG_AVP_FAIL"
                continue
            entry["measurable"] = True

            kills = {}
            for mid, mut_fn in mutants:
                signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(MUTANT_TIMEOUT_S)
                try:
                    mut_fail = call_avp_repeated(mut_fn, mr, EPSILON_AVP,
                                                 repeats=REPEATS) == AVPResult.FAIL
                    kills[mid] = bool(mut_fail)
                except _Timeout:
                    kills[mid] = False
                    rec["log"].append(f"{key} {mid}: AVP_TIMEOUT->not_killed")
                except Exception as e:  # noqa: BLE001
                    kills[mid] = False
                    rec["log"].append(f"{key} {mid}: AVP_ERROR {str(e)[:80]}")
                finally:
                    signal.alarm(0)
            entry["kills"] = kills
            n = len(mutants)
            rec["sms"][key] = (sum(kills.values()) / n) if n else None

    for cond in ("ALN", "CRS"):
        vals = [rec["sms"][f"set{s}_{cond}"] for s in SETS
                if rec["conditions"][f"set{s}_{cond}"]["measurable"]
                and rec["sms"].get(f"set{s}_{cond}") is not None]
        rec["sms"][f"{cond}_mean"] = (sum(vals) / len(vals)) if vals else None
        rec["sms"][f"{cond}_n_sets"] = len(vals)
    return rec


def build_analysis_inputs(cells: list[dict]) -> None:
    OUT_INPUTS.mkdir(parents=True, exist_ok=True)

    units = []
    excluded = []
    for c in cells:
        for cond, pred in (("ALN", True), ("CRS", False)):
            sms = c["sms"].get(f"{cond}_mean")
            if sms is None:
                excluded.append({"cell": c["cell"], "condition": cond,
                                 "reason": "no measurable set replicate"})
                continue
            units.append({"cell": c["cell"], "condition": cond,
                          "predicted_nonzero": pred, "observed_sms": sms})
    (OUT_INPUTS / "hzero_input.json").write_text(json.dumps(
        {"units": units, "excluded": excluded}, indent=2))

    pairs = []
    pair_excluded = []
    for c in cells:
        a, x = c["sms"].get("ALN_mean"), c["sms"].get("CRS_mean")
        if a is None or x is None:
            pair_excluded.append({"cell": c["cell"],
                                  "reason": f"ALN_mean={a} CRS_mean={x}"})
            continue
        pairs.append({"cell": c["cell"], "sms_aln": a, "sms_crs": x})
    (OUT_INPUTS / "hdisc_input.json").write_text(json.dumps(
        {"pairs": pairs, "excluded": pair_excluded}, indent=2))

    kills = []
    for c in cells:
        for key, entry in c["conditions"].items():
            if not entry["measurable"]:
                continue
            for mid, killed in entry["kills"].items():
                if killed:
                    kills.append({"cell": c["cell"], "mutant": mid,
                                  "mutant_stratum": c["mutant_stratum"],
                                  "mr_stratum": entry["mp"]})
    (OUT_INPUTS / "hxi_input.json").write_text(json.dumps(
        {"kills": kills, "hzero_verdict": None,
         "note": "hzero_verdict to be injected from hzero_results before running analysis_hxi"},
        indent=2))
    print(f"analysis inputs: {len(units)} H-ZERO units ({len(excluded)} excluded), "
          f"{len(pairs)} H-DISC pairs ({len(pair_excluded)} excluded), "
          f"{len(kills)} kill events")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cells", type=str, default=None)
    args = ap.parse_args()

    todo = APPLICABLE_CELLS
    if args.cells:
        want = {tuple(x.split(":")) for x in args.cells.split(",")}
        todo = [c for c in APPLICABLE_CELLS if c in want]
        assert todo

    t0 = time.time()
    results: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(eval_cell, op, put): (op, put) for op, put in todo}
        for fut in as_completed(futs):
            op, put = futs[fut]
            rec = fut.result()
            results[rec["cell"]] = rec
            s = rec["sms"]
            print(f"  {rec['cell']}: pool={len(rec['pool'])} "
                  f"ALN={s.get('ALN_mean')} ({s.get('ALN_n_sets')} sets) "
                  f"CRS={s.get('CRS_mean')} ({s.get('CRS_n_sets')} sets)", flush=True)

    ordered = [results[f"{op}×{put}"] for op, put in todo if f"{op}×{put}" in results]
    spec = {
        "conditions": "ALN = held-out MR of ALIGNED_MP[op]; CRS = held-out MR of CROSS_MP[op]",
        "aligned_map": ALIGNED_MP,
        "cross_map_cyclic": CROSS_MP,
        "cross_rationale": ("fixed cyclic map (aligned mod 5)+1: cardinality-matched 1-vs-1 "
                            "conditions; matches the per-MP single-MR v4 anchors the power "
                            "simulation calibrated on; each stratum appears exactly once as a "
                            "cross target; fixed ex-ante before any kill execution"),
        "kill_predicate": f"AVP(S,mr)=PASS and AVP(s',mr)=FAIL, {REPEATS}-repeat majority (v4 K_avp)",
        "epsilon_avp": EPSILON_AVP,
        "denominator": "funnel-confirmed non-equivalent pool (Task 2.1), never re-judged here",
        "sets": list(SETS),
        "measurability": "slot won in prescreen AND AVP(S,mr)=PASS; unmeasurable excluded+logged, never imputed",
    }
    OUT_MATRIX.write_text(json.dumps({
        "spec": spec,
        "n_cells": len(ordered),
        "wall_s": round(time.time() - t0, 1),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cells": ordered,
    }, indent=2))
    print(f"Wrote {OUT_MATRIX} ({time.time()-t0:.0f}s)")

    if todo == APPLICABLE_CELLS:
        build_analysis_inputs(ordered)


if __name__ == "__main__":
    main()
