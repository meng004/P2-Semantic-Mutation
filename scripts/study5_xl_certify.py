#!/usr/bin/env python3
"""Study-5 Family-XL certification gate + greedy roster walk (Amendment A1).

Implements PREREGISTRATION_STUDY5_v1.md §2b Step 5 + §2c exactly:

- walks the registered deterministic candidate ranking
  (src/p2/xlport/registry.py, Step-4 total order);
- for every candidate pair runs the registered dense-grid differential check:
  201-point grid x_i = i/200, PASS iff for all i
  |y_L(x_i) - y_py(x_i)| <= tol * max(|y_py(x_i)|, 1) with both sides finite,
  tol = 1e-6 unless the pair carries a pre-declared §2c class-1 exception
  (declared in the registry BEFORE this run; ceiling 1e-5);
- pairs failing the gate are EXCLUDED and disclosed (no fixing of external
  code, no re-certification path);
- greedy stop: after a program's pairs are certified, stop when certified
  pairs >= n_target (20) AND every stratum family is instantiable on >= 2
  certified programs; hard cap 28 pairs; floor 12 (shortfall would be
  disclosed, gates cannot be moved);
- writes the per-pair certification SSOT
  data/results/study5_xl_certification.json and the frozen roster
  configs/xl_roster.json (schema fixed by compute_hlang_delta.load_xl_roster).

Usage: PYTHONPATH=src python3 scripts/study5_xl_certify.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2.xlport import XlBuildError, load_pair, load_pyref  # noqa: E402
from p2.xlport import registry as R  # noqa: E402

OUT_CERT = ROOT / "data" / "results" / "study5_xl_certification.json"
OUT_ROSTER = ROOT / "configs" / "xl_roster.json"

# Frozen §4a primary-DGP power curve (read-off table; no post-data simulation).
POWER_CURVE = {8: 0.3826, 10: 0.5118, 12: 0.6114, 16: 0.7632,
               20: 0.8484, 24: 0.9036, 28: 0.9481}


def read_off_power(n: int):
    tab = [k for k in sorted(POWER_CURVE) if k <= n]
    if not tab:
        return None, None
    k = max(tab)
    return k, POWER_CURVE[k]


def certify_pair(pair_id: str, program_name: str, tol: float) -> dict:
    rec = dict(pair=pair_id, program=program_name, tol=tol,
               n_grid=R.GRID_N, status=None, max_rel_dev=None,
               argmax_x=None, n_nonfinite_L=0, n_nonfinite_py=0)
    try:
        prog_l = load_pair(pair_id)
        _ = prog_l.cmd  # force build
    except (XlBuildError, FileNotFoundError) as e:
        rec["status"] = "BUILD_FAIL"
        rec["build_error"] = str(e)[:1500]
        return rec
    prog_py = load_pyref(program_name)
    max_dev, argmax = -1.0, None
    nfl = nfp = 0
    t0 = time.time()
    for i in range(R.GRID_N):
        x = i / 200.0
        y_l = prog_l(x)
        try:
            y_p = float(prog_py(x))
        except Exception:
            y_p = math.nan
        if not math.isfinite(y_l):
            nfl += 1
            continue
        if not math.isfinite(y_p):
            nfp += 1
            continue
        dev = abs(y_l - y_p) / max(abs(y_p), 1.0)
        if dev > max_dev:
            max_dev, argmax = dev, x
    prog_l.close()
    rec["max_rel_dev"] = max_dev if max_dev >= 0 else None
    rec["argmax_x"] = argmax
    rec["n_nonfinite_L"] = nfl
    rec["n_nonfinite_py"] = nfp
    rec["elapsed_s"] = round(time.time() - t0, 2)
    ok = (nfl == 0 and nfp == 0 and max_dev >= 0 and max_dev <= tol)
    rec["status"] = "PASS" if ok else "FAIL"
    return rec


def coverage_ok(certified_programs: list[dict]) -> tuple[bool, dict]:
    counts = {mp: 0 for mp in (1, 2, 3, 4, 5)}
    for cand in certified_programs:
        for mp in cand["instantiable"]:
            counts[mp] += 1
    return all(v >= 2 for v in counts.values()), counts


def main() -> int:
    assert R.rank_check(), "registry violates the registered Step-4 rank order"
    records = []
    certified_pairs = []      # pair ids, walk order
    certified_cands = []      # candidate dicts with >=1 certified pair
    stopped = None

    for cand in R.CANDIDATES:
        if stopped:
            for p in cand["pairs"]:
                records.append(dict(pair=p["pair"], program=cand["program"],
                                    status="NOT_REACHED",
                                    note="greedy walk stopped before this candidate (S2b Step 5)"))
            continue
        tol = R.TOL_DEFAULT
        if cand.get("exception"):
            tol = max(R.TOL_DEFAULT, float(cand["exception"]["tol"]))
        cand_pass = 0
        for p in cand["pairs"]:
            if len(certified_pairs) >= R.N_CAP:
                records.append(dict(pair=p["pair"], program=cand["program"],
                                    status="NOT_REACHED", note="cap 28 reached"))
                continue
            print(f"[certify] {p['pair']:16s} tol={tol:g} ...",
                  end=" ", flush=True)
            rec = certify_pair(p["pair"], cand["program"], tol)
            rec.update(language=p["language"], upstream=R.UPSTREAM[p["upstream"]],
                       files=p.get("files", []), primary_mp=cand["primary_mp"],
                       source_idx=cand["src"], source=R.SOURCES[cand["src"]],
                       rank=(cand["c"], cand["l"], cand["src"], cand["program"]),
                       exception=cand.get("exception"),
                       aux=cand["aux"])
            if p.get("note"):
                rec["note"] = p["note"]
            records.append(rec)
            print(rec["status"],
                  f"max_dev={rec.get('max_rel_dev')!r} argmax={rec.get('argmax_x')!r}")
            if rec["status"] == "PASS":
                certified_pairs.append(p["pair"])
                cand_pass += 1
        if cand_pass:
            certified_cands.append(cand)
        cov, counts = coverage_ok(certified_cands)
        if len(certified_pairs) >= R.N_TARGET and cov:
            stopped = (f"target reached after program '{cand['program']}': "
                       f"certified n={len(certified_pairs)} >= {R.N_TARGET}, "
                       f"coverage >= 2 programs per family")
        if len(certified_pairs) >= R.N_CAP:
            stopped = stopped or f"cap {R.N_CAP} reached"

    n = len(certified_pairs)
    cov, counts = coverage_ok(certified_cands)
    read_n, read_power = read_off_power(n)
    langs = sorted({r["language"] for r in records
                    if r.get("status") == "PASS"})

    summary = dict(
        registration="PREREGISTRATION_STUDY5_v1.md S2b/S2c (Amendment A1)",
        rank_rule=R.RANK_RULE,
        grid="x_i = i/200, i=0..200 (201 points)",
        tolerance_rule="|y_L - y_py| <= tol * max(|y_py|, 1), both finite; tol=1e-6 unless pre-declared S2c class-1 exception (ceiling 1e-5)",
        n_floor=R.N_FLOOR, n_target=R.N_TARGET, n_cap=R.N_CAP,
        achieved_certified_n=n,
        floor_met=n >= R.N_FLOOR,
        under_certified_gate_n8=n < 8,
        family_instantiability_coverage=counts,
        coverage_ok=cov,
        languages_certified=langs,
        stop_reason=stopped or "candidate sweep exhausted (shortfall disclosed)",
        power_read_off=dict(largest_tabulated_n_le_achieved=read_n,
                            power=read_power,
                            curve="S4a primary (deflated) DGP, frozen"),
        certified_pairs_in_walk_order=certified_pairs,
    )

    OUT_CERT.parent.mkdir(parents=True, exist_ok=True)
    OUT_CERT.write_text(json.dumps(dict(summary=summary, pairs=records),
                                   indent=1))
    print(f"\n[write] {OUT_CERT}")

    roster_pairs = {}
    for rec in records:
        if rec.get("status") != "PASS":
            continue
        roster_pairs[rec["pair"]] = dict(
            primary_mp=rec["primary_mp"],
            program=rec["program"],
            language=rec["language"],
            source=rec["source"],
            upstream=rec["upstream"],
            files=rec["files"],
            certification=dict(max_rel_dev=rec["max_rel_dev"],
                               tol=rec["tol"], grid_n=rec["n_grid"]),
        )
    roster = dict(
        meta=dict(amendment="A1 (scheduled, pre-mutant)",
                  frozen_by="scripts/study5_xl_certify.py",
                  registration="PREREGISTRATION_STUDY5_v1.md S2b/S2c",
                  achieved_certified_n=n,
                  spec_doc="docs/prereg_v2/STUDY5_XL_ROSTER.md"),
        pairs=roster_pairs,
    )
    OUT_ROSTER.write_text(json.dumps(roster, indent=1))
    print(f"[write] {OUT_ROSTER}")
    print(f"\nachieved certified n = {n} (floor {R.N_FLOOR}, target "
          f"{R.N_TARGET}, cap {R.N_CAP}); languages: {', '.join(langs)}")
    print(f"family instantiability coverage (certified programs): {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
