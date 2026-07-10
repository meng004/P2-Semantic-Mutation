#!/usr/bin/env python3
"""POST-HOC cluster-inference sensitivity — PUT-block bootstrap reanalysis.

STATUS: POST-HOC SENSITIVITY (2026-07-10). This script responds to the
author's editorial review of the P1 cluster-inference concern and was written
AFTER all confirmatory data and verdicts were closed. It is NOT a registered
analyzer and it changes NO registered verdict:

  * The registered cell-level verdicts stand exactly as recorded in their
    frozen SSOTs (dualblind_delta_delta_v5/v7.json, hlang_delta_v7c.json,
    rq2_cliffs_delta_v4_mp5.json).
  * The PUT-cluster CIs computed here SUPERSEDE the cell-level CIs for
    manuscript citation (the interval the paper quotes), because the
    cell-level intervals resample the 5 cells of one PUT as if independent.

THE PROBLEM BEING FIXED. The frozen H2-1'/H2-1/H-LANG bootstrap
(compute_dualblind_delta.boot_delta_distribution) is a multinomial two-sample
bootstrap over CELLS: it treats the 28 aligned + 112 cross cells (Study 2/4)
as 140 independent observations. But the five cells of one PUT share the PUT's
mutant pool and program semantics, so they are correlated; the exchangeable
sampling unit is the PUT, not the cell. The correct scheme is a PUT-block
bootstrap: resample PUTs with replacement, keep each resampled PUT's five
cells intact (1 aligned + 4 cross), and recompute Cliff's delta per replicate.

ALREADY-CORRECT ANALYSES (documented, not recomputed as new results):
  * H2-2 Delta-delta (compute_dualblind_delta.paired_bootstrap_dd) already
    block-resamples the PUT list and applies the SAME resample to both arms
    (paired-role bootstrap). It was cluster-correct as registered; this script
    merely re-executes the frozen function to verify byte-agreement with the
    committed SSOT and records that fact.
  * H2-4 delta_MR (compute_mr_diversity_delta.boot_mean_distribution) is a
    PUT-level block bootstrap by construction (not re-verified here; the
    Family-MR wave is HALTED per the author's directive).

BOUNDED-NULL FORMALIZATION (editorial item 3). For H2-2 the sound rule for a
"no effect of magnitude >= 0.20" claim is CI \\subset [-0.20, +0.20]. The
registered rule (CI contains 0 AND half-width <= 0.14) does NOT logically
imply containment in general: e.g. CI = [-0.001, +0.279] contains 0 and has
half-width 0.14 but its upper end exceeds +0.20. For the achieved v7 CI
[-0.021, +0.0686] containment HOLDS, so the registered verdict is also sound
under the correct rule. This is recorded in the output JSON.

Constants deliberately match the registered analysis stack: B = 10,000,
master seed 20260708, PRIMARY_CELLS_V3 (v3b prohibited). All estimand
machinery (Cliff's delta, exclusion rule, cell parsing, primary-MP rule) is
IMPORTED from the frozen compute_dualblind_delta.py so no measurement drifts.

Inputs (all CLOSED, read-only):
  data/results/sms_track2_v5.json           Study-2 v5 H2-1' grid
  data/results/sms_track2_v7.json           Study-4 v7 cross-source arm
  data/results/sms_track2_v7_same.json      Study-4 v7 same-source arm
  data/results/sms_track2_v7c.json          Study-4 C-port pool (H-LANG)
  data/results/sms_track2_v4.json           Study-1 v4 pool
  data/results/dualblind_delta_delta_v5.json   committed cell-level CIs (v5)
  data/results/dualblind_delta_delta_v7.json   committed cell-level CIs (v7)
  data/results/hlang_delta_v7c.json            committed cell-level CI (C)
  data/results/rq2_cliffs_delta_v4_mp5.json    committed cell-level CI (v4)
Output:
  data/results/cluster_sensitivity_v1.json

Usage:
    PYTHONPATH=src python3 scripts/compute_cluster_sensitivity.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "data" / "results"

# ---- constants: identical to the registered stack (never re-tuned) ----------
MASTER_SEED = 20260708
B_BOOT = 10_000
DD_MAGNITUDE = 0.20            # H2-2 registered magnitude of interest
DD_HALFWIDTH_BOUND = 0.14      # H2-2 registered bounded-null half-width gate
C_GRID_PUTS = ("a1", "a2", "a3", "b1", "b2", "b3", "c2")   # H-LANG grid

OUT = RESULTS / "cluster_sensitivity_v1.json"


# --------------------------------------------------------------------------- #
# Frozen estimand machinery, imported (never re-implemented)
# --------------------------------------------------------------------------- #
def _load_dualblind_module():
    spec = importlib.util.spec_from_file_location(
        "compute_dualblind_delta", ROOT / "scripts" / "compute_dualblind_delta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DBD = _load_dualblind_module()
cliffs_delta = _DBD.cliffs_delta
per_put_slices = _DBD.per_put_slices
split_aligned_cross = _DBD.split_aligned_cross
_is_excluded = _DBD._is_excluded
_parse_cell = _DBD._parse_cell
PRIMARY = _DBD.PRIMARY                       # PRIMARY_CELLS_V3 (v3b prohibited)


def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def per_put_slices_grid(sms: dict, grid) -> dict:
    """per_put_slices restricted to a PUT grid (H-LANG C grid)."""
    out: dict[str, tuple[list, list]] = {}
    for cell, v in sms.items():
        put, mp = _parse_cell(cell)
        if put not in grid:
            continue
        if _is_excluded(v):
            continue
        a, c = out.setdefault(put, ([], []))
        (a if mp == PRIMARY[put] else c).append(float(v["sms"]))
    return out


# --------------------------------------------------------------------------- #
# PUT-block bootstrap (the cluster-correct scheme)
# --------------------------------------------------------------------------- #
def put_block_boot_delta(slices: dict, B: int = B_BOOT,
                         seed: int = MASTER_SEED) -> np.ndarray:
    """PUT-block bootstrap of the aligned-vs-cross Cliff's delta.

    Resample the PUT list with replacement (block = the PUT: its aligned and
    cross cells travel together, intact), recompute delta per replicate.
    """
    puts = sorted(slices)
    n = len(puts)
    if n == 0:
        return np.zeros(B)
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, size=n)
        aligned = [x for j in idx for x in slices[puts[j]][0]]
        cross = [x for j in idx for x in slices[puts[j]][1]]
        out[i] = cliffs_delta(aligned, cross)
    return out


def cluster_block(slices: dict, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    dist = put_block_boot_delta(slices, B=B, seed=seed)
    return {
        "scheme": "PUT-block bootstrap: resample PUTs with replacement, keep "
                  "each PUT's cells intact, recompute Cliff's delta per replicate",
        "n_puts": len(slices),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "one_sided_95_lower_bound": round(float(np.quantile(dist, 0.05)), 4),
        "two_sided_ci95": [round(float(np.quantile(dist, 0.025)), 4),
                           round(float(np.quantile(dist, 0.975)), 4)],
    }


def _direction_note(point: float, cluster_lower: float,
                    registered_verdict: str, confirmatory: bool) -> str:
    survives = cluster_lower > 0.0
    if confirmatory:
        if registered_verdict == "CONFIRM" and survives:
            return ("NO IMPACT: the registered CONFIRM direction survives "
                    "clustering (PUT-cluster one-sided 95% lower bound > 0). "
                    "Cluster CI supersedes the cell-level CI for citation.")
        if registered_verdict == "CONFIRM" and not survives:
            return ("IMPACT: the registered CONFIRM does NOT survive "
                    "clustering (PUT-cluster lower bound <= 0); must be "
                    "disclosed as overturned by the corrected inference.")
        if registered_verdict == "NOT_CONFIRMED" and not survives:
            return ("NO IMPACT: registered NOT_CONFIRMED; the PUT-cluster "
                    "lower bound is also <= 0, so the negative verdict stands "
                    "a fortiori under the corrected inference.")
        return ("NOTE: registered NOT_CONFIRMED but the PUT-cluster lower "
                "bound > 0. The registered verdict STANDS (no post-hoc "
                "promotion); recorded for transparency only.")
    # descriptive (Study-1 headline): direction statement only
    return ("Descriptive contrast (no registered one-sided verdict): "
            f"direction {'survives' if survives else 'does not survive'} "
            "clustering; cluster CI supersedes the cell-level CI for citation.")


# --------------------------------------------------------------------------- #
# Analyses (a) - (f)
# --------------------------------------------------------------------------- #
def analysis_h21_style(pool_path: Path, committed: dict, label: str,
                       grid=None, committed_note: str = "",
                       confirmatory: bool = True,
                       B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    sms = load_json(pool_path)
    slices = (per_put_slices(sms) if grid is None
              else per_put_slices_grid(sms, grid))
    aligned = [x for p in slices for x in slices[p][0]]
    cross = [x for p in slices for x in slices[p][1]]
    point = round(cliffs_delta(aligned, cross), 4)
    committed_point = committed.get("point")
    if committed_point is not None and abs(point - committed_point) > 5e-5:
        raise AssertionError(
            f"{label}: recomputed point delta {point} != committed "
            f"{committed_point} — input SSOT drift, aborting")
    cluster = cluster_block(slices, B=B, seed=seed)
    verdict = committed.get("verdict", "(descriptive)")
    return {
        "input_pool": _rel(pool_path),
        "n_aligned": len(aligned),
        "n_cross": len(cross),
        "point_cliffs_delta": point,
        "cell_level_as_committed": {**committed, "note": committed_note or (
            "cell-level multinomial two-sample bootstrap; treats cells of one "
            "PUT as independent (the flagged issue)")},
        "put_cluster": cluster,
        "registered_verdict": verdict,
        "verdict_impact": _direction_note(
            point, cluster["one_sided_95_lower_bound"], verdict, confirmatory),
    }


def analysis_h22_dd(B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    """(d) H2-2 Delta-delta: verify the frozen bootstrap was ALREADY
    cluster-correct by re-executing the frozen paired_bootstrap_dd."""
    committed = load_json(RESULTS / "dualblind_delta_delta_v7.json")
    h22 = committed["H2_2_source_diversity_dual_blind"]
    cross_slices = per_put_slices(load_json(RESULTS / "sms_track2_v7.json"))
    same_slices = per_put_slices(load_json(RESULTS / "sms_track2_v7_same.json"))
    puts = sorted(set(cross_slices) & set(same_slices))
    point, lo, hi, _ = _DBD.paired_bootstrap_dd(
        cross_slices, same_slices, puts, B=B, seed=seed)
    repro = {"delta_delta_point": round(point, 4),
             "ci95_two_sided": [round(lo, 4), round(hi, 4)]}
    if (repro["delta_delta_point"] != h22["delta_delta_point"]
            or repro["ci95_two_sided"] != h22["ci95_two_sided"]):
        raise AssertionError(
            f"H2-2 reproduction mismatch: {repro} vs committed "
            f"{{'delta_delta_point': {h22['delta_delta_point']}, "
            f"'ci95_two_sided': {h22['ci95_two_sided']}}}")
    ci_lo, ci_hi = h22["ci95_two_sided"]
    contained = (ci_lo >= -DD_MAGNITUDE) and (ci_hi <= DD_MAGNITUDE)
    return {
        "inputs": ["data/results/sms_track2_v7.json",
                   "data/results/sms_track2_v7_same.json"],
        "already_cluster_correct": True,
        "how": "the frozen compute_dualblind_delta.paired_bootstrap_dd "
               "block-resamples the shared 28-PUT list with replacement and "
               "applies the SAME resample to both arms (paired-role "
               "bootstrap); the resampling unit was the PUT from the start, "
               "so NO cluster correction is needed for H2-2",
        "n_puts_paired": h22["n_puts_paired"],
        "delta_delta_point": h22["delta_delta_point"],
        "ci95_two_sided": h22["ci95_two_sided"],
        "ci95_half_width": h22["ci95_half_width"],
        "reproduction_check": "frozen paired_bootstrap_dd re-executed "
                              "(B=10000, seed 20260708); point and CI match "
                              "the committed SSOT exactly",
        "registered_verdict": h22["verdict"],
        "verdict_impact": "NO IMPACT: H2-2 was already PUT-clustered as "
                          "registered; the committed BOUNDED_NULL verdict and "
                          "CI are unchanged and remain citable as-is",
        "bounded_null_formalization": {
            "achieved_ci": h22["ci95_two_sided"],
            "sound_rule": f"CI subset of [-{DD_MAGNITUDE}, +{DD_MAGNITUDE}]",
            "sound_rule_holds": bool(contained),
            "registered_rule": "CI contains 0 AND half-width <= "
                               f"{DD_HALFWIDTH_BOUND}",
            "registered_rule_flag": (
                "the registered rule does NOT logically imply containment in "
                "[-0.20, +0.20] in general: a CI of [-0.001, +0.279] contains "
                "0 with half-width 0.14 yet its upper end exceeds +0.20. For "
                "the achieved CI [-0.021, +0.0686] containment HOLDS, so the "
                "BOUNDED_NULL verdict is also licensed by the sound rule; the "
                "manuscript should state the containment criterion, not the "
                "half-width heuristic."),
        },
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(out_path=OUT, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    d5 = load_json(RESULTS / "dualblind_delta_delta_v5.json")[
        "H2_1_aligned_dominates_cross"]
    d7 = load_json(RESULTS / "dualblind_delta_delta_v7.json")
    d7_h21 = d7["H2_1_aligned_dominates_cross"]
    d7_h22 = d7["H2_2_source_diversity_dual_blind"]
    hl = load_json(RESULTS / "hlang_delta_v7c.json")[
        "H_LANG_cross_language_invariance"]
    rq2 = load_json(RESULTS / "rq2_cliffs_delta_v4_mp5.json")

    a = analysis_h21_style(
        RESULTS / "sms_track2_v5.json",
        {"point": d5["cliffs_delta"],
         "one_sided_95_lower_bound": d5["one_sided_95_lower_bound"],
         "two_sided_ci95": d5["descriptive_only"]["two_sided_ci95"],
         "verdict": d5["verdict"],
         "source": "data/results/dualblind_delta_delta_v5.json"},
        "study2_v5_h2_1_prime", B=B, seed=seed)

    b = analysis_h21_style(
        RESULTS / "sms_track2_v7.json",
        {"point": d7_h21["cliffs_delta"],
         "one_sided_95_lower_bound": d7_h21["one_sided_95_lower_bound"],
         "two_sided_ci95": d7_h21["descriptive_only"]["two_sided_ci95"],
         "verdict": d7_h21["verdict"],
         "source": "data/results/dualblind_delta_delta_v7.json"},
        "study4_v7_h2_1_cross", B=B, seed=seed)

    # (c) same-source arm: no standalone committed CI exists (the arm enters
    # the record only as delta_same_source_arm inside H2-2), so the cell-level
    # comparator is recomputed here with the frozen H2-1 method.
    same_sms = load_json(RESULTS / "sms_track2_v7_same.json")
    same_a, same_c = split_aligned_cross(same_sms)
    same_dist = _DBD.boot_delta_distribution(same_a, same_c, B=B, seed=seed)
    c = analysis_h21_style(
        RESULTS / "sms_track2_v7_same.json",
        {"point": d7_h22["delta_same_source_arm"],
         "one_sided_95_lower_bound": round(float(np.quantile(same_dist, 0.05)), 4),
         "two_sided_ci95": [round(float(np.quantile(same_dist, 0.025)), 4),
                            round(float(np.quantile(same_dist, 0.975)), 4)],
         "verdict": "(descriptive arm)",
         "source": "point: dualblind_delta_delta_v7.json::delta_same_source_arm"},
        "study4_v7_same_arm",
        committed_note=("no standalone cell-level CI was committed for this "
                        "arm; the cell-level comparator here is recomputed "
                        "with the frozen H2-1 multinomial method (B=10000, "
                        "seed 20260708) for a like-for-like contrast"),
        confirmatory=False, B=B, seed=seed)

    d = analysis_h22_dd(B=B, seed=seed)

    e = analysis_h21_style(
        RESULTS / "sms_track2_v7c.json",
        {"point": hl["cliffs_delta_C"],
         "one_sided_95_lower_bound": hl["one_sided_95_lower_bound"],
         "two_sided_ci95": hl["descriptive_only"]["two_sided_ci95"],
         "verdict": hl["verdict"],
         "source": "data/results/hlang_delta_v7c.json"},
        "hlang_v7c_delta_C", grid=C_GRID_PUTS, B=B, seed=seed)

    f = analysis_h21_style(
        RESULTS / "sms_track2_v4.json",
        {"point": round(rq2["cliffs_delta"], 4),
         "one_sided_95_lower_bound": None,
         "two_sided_ci95": [round(rq2["delta_ci_95"][0], 4),
                            round(rq2["delta_ci_95"][1], 4)],
         "verdict": "(descriptive headline; no registered one-sided rule)",
         "source": "data/results/rq2_cliffs_delta_v4_mp5.json"},
        "study1_v4_mp5_headline",
        committed_note=("committed CI is the per-group cell resampling of "
                        "p2.stats.cliffs_delta.bootstrap_delta_ci (B=10000, "
                        "seed 42, no one-sided bound recorded); cells of one "
                        "PUT treated as independent (the flagged issue)"),
        confirmatory=False, B=B, seed=seed)

    report = {
        "artefact": "cluster_sensitivity_v1",
        "generated_by": "scripts/compute_cluster_sensitivity.py",
        "status": "POST-HOC SENSITIVITY (2026-07-10): responds to the "
                  "editorial review's cluster-inference concern (P1). NOT a "
                  "registered analyzer; written after all confirmatory "
                  "verdicts were closed.",
        "citation_policy": "the registered cell-level verdicts stand as "
                           "recorded in their frozen SSOTs; the PUT-cluster "
                           "CIs below SUPERSEDE the cell-level CIs for "
                           "manuscript citation",
        "issue": "the frozen H2-1'/H2-1/H-LANG multinomial bootstrap "
                 "resamples the 28 aligned + 112 cross CELLS as independent; "
                 "the five cells of one PUT are correlated (shared mutant "
                 "pool and program), so the exchangeable resampling unit is "
                 "the PUT (block bootstrap)",
        "master_seed": seed,
        "bootstrap_B": B,
        "primary_mp_rule": "PRIMARY_CELLS_V3 (imported from the frozen "
                           "compute_dualblind_delta.py; v3b prohibited)",
        "analyses": {
            "a_study2_v5_h2_1_prime": a,
            "b_study4_v7_h2_1_cross": b,
            "c_study4_v7_same_arm": c,
            "d_study4_h2_2_delta_delta": d,
            "e_hlang_v7c_delta_C": e,
            "f_study1_v4_mp5_headline": f,
        },
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2,
                                             ensure_ascii=False))
    return report


def _print(report: dict) -> None:
    print("=== POST-HOC cluster-inference sensitivity (PUT-block bootstrap) ===")
    for key, r in report["analyses"].items():
        if key == "d_study4_h2_2_delta_delta":
            print(f"[{key}] ALREADY cluster-correct; Delta-delta="
                  f"{r['delta_delta_point']:+.4f} CI {r['ci95_two_sided']} "
                  f"verdict {r['registered_verdict']} (unchanged)")
            bn = r["bounded_null_formalization"]
            print(f"    bounded-null: CI subset [-0.20,+0.20] holds = "
                  f"{bn['sound_rule_holds']}")
            continue
        cell = r["cell_level_as_committed"]
        cl = r["put_cluster"]
        print(f"[{key}] delta={r['point_cliffs_delta']:+.4f} | cell lower="
              f"{cell['one_sided_95_lower_bound']} CI {cell['two_sided_ci95']}"
              f" | cluster lower={cl['one_sided_95_lower_bound']:+.4f} "
              f"CI {cl['two_sided_ci95']} (n_puts={cl['n_puts']})")
        print(f"    {r['verdict_impact']}")


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
