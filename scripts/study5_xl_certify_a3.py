#!/usr/bin/env python3
"""Study-5 Family-XL Amendment A3: roster EXTENSION wave certification
(scale diversity, author-directed, pre-mutant).

Executes the A3 walk registered in ``src/p2/xlport/registry.py``
(A3_CANDIDATES, A3_SCALE_RULE, A3_GROUP_RULE) under the UNCHANGED
PREREGISTRATION_STUDY5_v1.md §2c certification gate (201-point grid,
|y_L - y_py| <= tol * max(|y_py|, 1), both finite, tol = 1e-6 unless a
pre-declared class-1 exception, ceiling 1e-5; one-shot, failures disclosed,
never fixed). The gate implementation is IMPORTED from the frozen A1 driver
``scripts/study5_xl_certify.py`` (``certify_pair``), so the check is
byte-identical to A1's.

Append-only outputs:
- ``configs/xl_roster.json``: new pairs appended; every A1 pair object is
  asserted deep-equal to its pre-run state; a top-level ``scale_stratum``
  map (function-level vs module-level, the disclosed stratification
  variable) is added covering ALL pairs old and new.
- ``data/results/study5_xl_certification.json``: A1 ``summary``/``pairs``
  blocks asserted unchanged; A3 results land in a new top-level ``a3``
  block.

Budget: N_CAP (28, registered cap) minus the achieved A1 n (21) = 7 new
pairs. The walk stops at the cap; candidates beyond it are NOT_REACHED.

Usage: PYTHONPATH=src python3 scripts/study5_xl_certify_a3.py
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p2.xlport import registry as R  # noqa: E402

OUT_CERT = ROOT / "data" / "results" / "study5_xl_certification.json"
OUT_ROSTER = ROOT / "configs" / "xl_roster.json"


def _load_a1_driver():
    spec = importlib.util.spec_from_file_location(
        "study5_xl_certify", ROOT / "scripts" / "study5_xl_certify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    a1 = _load_a1_driver()
    assert R.rank_check(), "A1 registry rank order violated"
    assert R.a3_rank_check(), "A3 registry walk order violated"

    roster = json.loads(OUT_ROSTER.read_text())
    a1_pairs_before = copy.deepcopy(roster["pairs"])
    n_a1 = len(a1_pairs_before)
    budget = R.N_CAP - n_a1
    assert budget == R.A3_NEW_PAIR_BUDGET, (budget, R.A3_NEW_PAIR_BUDGET)

    cert = json.loads(OUT_CERT.read_text())
    a1_cert_before = copy.deepcopy({"summary": cert["summary"],
                                    "pairs": cert["pairs"]})
    assert "a3" not in cert, "A3 block already present — one-shot rule"

    records = []
    new_pairs = []           # pair ids, walk order
    certified_cands = []     # A3 candidate dicts with >=1 certified pair
    halted = None

    for cand in R.A3_CANDIDATES:
        tol = R.TOL_DEFAULT
        if cand.get("exception"):
            tol = max(R.TOL_DEFAULT, float(cand["exception"]["tol"]))
        cand_pass = 0
        for p in cand["pairs"]:
            if halted or n_a1 + len(new_pairs) >= R.N_CAP:
                records.append(dict(pair=p["pair"], program=cand["program"],
                                    status="NOT_REACHED",
                                    note=halted or f"cap {R.N_CAP} reached"))
                continue
            shim_dir = ROOT / "src" / "p2" / "xlport" / "shims" / p["pair"]
            if not (shim_dir / "build.json").exists():
                # disclosed halt, never a silent candidate exclusion
                halted = (f"walk halted before pair {p['pair']}: shim "
                          "inventory exhausted (adapter not yet authored); "
                          "disclosed shortfall, walk NOT resumed")
                records.append(dict(pair=p["pair"], program=cand["program"],
                                    status="NOT_REACHED", note=halted))
                continue
            print(f"[certify-a3] {p['pair']:16s} tol={tol:g} ...",
                  end=" ", flush=True)
            rec = a1.certify_pair(p["pair"], cand["program"], tol)
            rec.update(language=p["language"],
                       upstream=R.UPSTREAM[p["upstream"]],
                       files=p.get("files", []),
                       primary_mp=cand["primary_mp"],
                       source_idx=cand["src"], source=R.SOURCES[cand["src"]],
                       rank=(cand["group"], cand["c"], cand["l"],
                             cand["src"], cand["program"]),
                       exception=cand.get("exception"),
                       aux=cand["aux"],
                       scale=R.A3_SCALE,
                       scale_evidence=cand["scale_evidence"],
                       amendment="A3")
            if p.get("note"):
                rec["note"] = p["note"]
            records.append(rec)
            print(rec["status"],
                  f"max_dev={rec.get('max_rel_dev')!r} "
                  f"argmax={rec.get('argmax_x')!r}")
            if rec["status"] == "PASS":
                new_pairs.append(p["pair"])
                cand_pass += 1
        if cand_pass:
            certified_cands.append(cand)

    n_total = n_a1 + len(new_pairs)
    read_n, read_power = a1.read_off_power(n_total)

    # combined per-family instantiability coverage over certified PROGRAMS
    a1_certified_programs = {v["program"] for v in a1_pairs_before.values()}
    a1_cands = [c for c in R.CANDIDATES
                if c["program"] in a1_certified_programs]
    cov_counts = {mp: 0 for mp in (1, 2, 3, 4, 5)}
    for cand in a1_cands + certified_cands:
        for mp in cand["instantiable"]:
            cov_counts[mp] += 1

    langs_new = sorted({r["language"] for r in records
                        if r.get("status") == "PASS"})

    summary = dict(
        registration=("PREREGISTRATION_STUDY5_v1.md S2b/S2c gate unchanged; "
                      "Amendment A3 (author-directed roster EXTENSION wave, "
                      "scale diversity, pre-mutant)"),
        directive=("add module/pipeline-scale production-library pairs; "
                   "P1/P2 in force; priorities (a) module scale, "
                   "(b) MP2/MP5 primary-coverage repair"),
        scale_rule=R.A3_SCALE_RULE,
        group_rule=R.A3_GROUP_RULE,
        rank_rule=R.RANK_RULE + " (within each A3 group)",
        grid="x_i = i/200, i=0..200 (201 points)",
        tolerance_rule=("|y_L - y_py| <= tol * max(|y_py|, 1), both finite; "
                        "tol=1e-6 unless pre-declared S2c class-1 exception "
                        "(ceiling 1e-5); one-shot, failures disclosed"),
        n_cap=R.N_CAP, n_a1=n_a1, new_pair_budget=budget,
        achieved_new_pairs=len(new_pairs),
        achieved_total_n=n_total,
        cap_respected=n_total <= R.N_CAP,
        family_instantiability_coverage_certified_programs=cov_counts,
        languages_certified_a3=langs_new,
        walk_halt=halted,
        power_read_off=dict(largest_tabulated_n_le_achieved=read_n,
                            power=read_power,
                            curve="S4a primary (deflated) DGP, frozen"),
        new_pairs_in_walk_order=new_pairs,
        pilot_note=("the registered v8xl_pilot pairs (invsqrt.cpp, brent.c) "
                    "are determined by the A1 walk order, which precedes "
                    "every A3 pair; the pilot determination is unchanged by "
                    "this wave and no A3 pair carries any mutant"),
    )

    # ---- append to the certification SSOT (A1 blocks byte-identical) ---- #
    assert cert["summary"] == a1_cert_before["summary"]
    assert cert["pairs"] == a1_cert_before["pairs"]
    cert["a3"] = dict(summary=summary, pairs=records)
    OUT_CERT.write_text(json.dumps(cert, indent=1))
    print(f"\n[write] {OUT_CERT}")

    # ---- append to the roster (A1 pair objects deep-equal asserted) ----- #
    for rec in records:
        if rec.get("status") != "PASS":
            continue
        assert rec["pair"] not in roster["pairs"], rec["pair"]
        roster["pairs"][rec["pair"]] = dict(
            primary_mp=rec["primary_mp"],
            program=rec["program"],
            language=rec["language"],
            source=rec["source"],
            upstream=rec["upstream"],
            files=rec["files"],
            certification=dict(max_rel_dev=rec["max_rel_dev"],
                               tol=rec["tol"], grid_n=rec["n_grid"]),
            scale=R.A3_SCALE,
            amendment="A3",
        )
    for pid, entry in a1_pairs_before.items():
        assert roster["pairs"][pid] == entry, f"A1 entry mutated: {pid}"
    roster["scale_stratum"] = {
        pid: (R.A1_SCALE if pid in a1_pairs_before else R.A3_SCALE)
        for pid in roster["pairs"]
    }
    roster["meta"]["amendment"] = ("A1 (scheduled, pre-mutant) + A3 "
                                   "(author-directed scale-extension wave, "
                                   "pre-mutant)")
    roster["meta"]["achieved_certified_n"] = len(roster["pairs"])
    roster["meta"]["a3"] = dict(
        frozen_by="scripts/study5_xl_certify_a3.py",
        new_pairs=new_pairs,
        new_pair_budget=budget,
        scale_stratum_note=("scale_stratum (top-level) is the disclosed "
                            "stratification variable for every pair old and "
                            "new; A1 pair objects are byte-unchanged"),
    )
    OUT_ROSTER.write_text(json.dumps(roster, indent=1))
    print(f"[write] {OUT_ROSTER}")

    prim = {mp: 0 for mp in (1, 2, 3, 4, 5)}
    for v in roster["pairs"].values():
        prim[int(v["primary_mp"])] += 1
    print(f"\nachieved total n = {n_total} (A1 {n_a1} + A3 "
          f"{len(new_pairs)}; cap {R.N_CAP})")
    print(f"primary-cell distribution (all pairs): {prim}")
    print(f"scale strata: function={n_a1}, module={len(new_pairs)}")
    print(f"instantiability coverage (certified programs): {cov_counts}")
    print(f"power read-off: n<={n_total} -> tabulated n={read_n}, "
          f"power={read_power}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
