#!/usr/bin/env python3
"""Study-4 confirmatory analysis — H-LANG cross-language invariance (RQ-S4c).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md (§3.3, §7b contract;
Amendment v1.1) BEFORE any Study-4 C-port data generation. Any post-data
modification of this script MUST be disclosed as a deviation in the registration
§10 appendix.

    ┌─────────────────────────────────────────────────────────────────────┐
    │ PRE-FROZEN SCORER — no Study-4 C mutant, C SMS cell, or delta_C       │
    │ outcome existed when this file was frozen. The decision rule below    │
    │ (confirm iff one_sided_95_lower_bound > 0) is the registered a-priori │
    │ rule; changing the estimand or threshold after any C outcome is       │
    │ visible is a protocol violation (registration §5d, §8).               │
    └─────────────────────────────────────────────────────────────────────┘

Implements EXACTLY the registered H-LANG (Family L) verdict
(PREREGISTRATION_STUDY4_v1.md §3.3, §7b):

  On the ACHIEVED C port of the 7 original Study-1 PUTs (a1,a2,a3,b1,b2,b3,c2;
  the 5 sklearn kernels c1/c3/d1/d2/d3 are unportable, C_PORT_SPEC.md §3;
  amendment v1.1), split the per-cell SMS into

      aligned  = cells whose MP == the PUT's primary MP (PRIMARY_CELLS_V3,
                 mapped cell-for-cell to the C cells: a→MP1, b→MP2, c→MP5),
      cross    = all other adjudicated cells,

  compute the two-sample Cliff's delta_C = P(aligned > cross) - P(aligned <
  cross), and its one-sided 95% percentile-bootstrap LOWER bound (multinomial
  two-sample bootstrap, B=10,000, seed 20260708).

    Decision (FROZEN) = CONFIRM cross-language invariance iff
                        one_sided_95_lower_bound > 0.

BOOTSTRAP IS BYTE-IDENTICAL TO H2-1'.  The estimand, the split, and the
resampling scheme are the SAME as compute_dualblind_delta.analyze_h2_1 (the
Study-2 aligned>cross confirmatory test); this scorer imports
``cliffs_delta`` / ``boot_delta_distribution`` / ``_is_excluded`` / ``_parse_cell``
/ ``PRIMARY`` from that frozen module rather than re-implementing them, so no
measurement can drift between the Python and C legs. The only difference is the
grid: H-LANG restricts to the 7 C PUTs and reads the C-port pool.

Power (amendment v1.1): 0.6865 at n=7 from the v5-calibrated DGP (true delta
0.4385); below the 0.80 target and DISCLOSED — the estimand is a direction
claim, and H-LANG stays confirmatory with the achieved power disclosed
(power_study4.json::c...power_delta_gt0_at_n7). NO threshold moved.

EXCLUSIONS (§7b). Vacant / non-adjudicated / null-SMS cells are dropped
(``_is_excluded``, shared with the Python leg). The Python calibration pilot
{a2, b4} firewall does NOT apply here: H-LANG is a distinct C-port estimand and
the C-side data is fresh; a2 is confirmatory in the C grid (amendment v1.1 §0.3).

Inputs (registration §7b):
  C-port per-cell SMS pool : data/results/sms_track2_v7c.json (fresh validated
                             C pool; each cell carries an ``sms`` scalar)
Output:
  data/results/hlang_delta_v7c.json  (verdict + licensed string)

Usage:
    PYTHONPATH=src python3 scripts/compute_hlang_delta.py
    PYTHONPATH=src python3 scripts/compute_hlang_delta.py \
        --matrix data/results/sms_track2_v7c.json \
        --out    data/results/hlang_delta_v7c.json

STUDY-5 ADDITIVE PRESET (PREREGISTRATION_STUDY5_v1.md §6; the default Study-4
path above is byte-unchanged):
    PYTHONPATH=src python3 scripts/compute_hlang_delta.py --study5-family xl
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

# ---- registered constants (PREREGISTRATION_STUDY4_v1.md §3.3, §7b) ----------
MASTER_SEED = 20260708          # registration master seed (§7)
B_BOOT = 10_000                 # bootstrap resamples (§3.3, byte-identical to H2-1')
# Achieved C-port grid (amendment v1.1; a2 RETAINED confirmatory).
C_GRID_PUTS = ("a1", "a2", "a3", "b1", "b2", "b3", "c2")

MATRIX = RESULTS / "sms_track2_v7c.json"
OUT = RESULTS / "hlang_delta_v7c.json"

# ---- STUDY-5 ADDITIVE PRESET (PREREGISTRATION_STUDY5_v1.md §6) ---------------
# Pre-frozen BEFORE any Study-5 data generation (no v8xl pool, no XL roster,
# no XL mutant exists). ADDITIVE ONLY: the default (Study-4 H-LANG, 7-PUT C
# grid, v7c paths) is byte-unchanged — same pattern as the Study-4
# `compute_h4_graded.py --pooled` additive contract. The Study-4 verdict
# artefact hlang_delta_v7c.json is CLOSED and is never recomputed through
# this preset.
#
# Family XL (H-LANG-2, cross-language EXTERNAL corpus) scores an externally
# sourced program-language-pair grid, so its roster and primary-stratum map
# do NOT live in PRIMARY_CELLS_V3: they are read from the frozen roster SSOT
# `configs/xl_roster.json` (frozen by the registered §2 selection protocol in
# a dated pre-data amendment, BEFORE any XL mutant generation). Roster format:
#   {"pairs": {"<PAIR_ID>": {"primary_mp": <1..5>, ...}, ...}, ...}
# Cell keys in the XL SMS pool follow the frozen convention
# f"{PAIR_ID}_MP{k}" (uppercase pair id), identical in shape to every prior
# pool, so _parse_cell / _is_excluded are reused byte-identically.
XL_ROSTER = ROOT / "configs" / "xl_roster.json"
XL_MIN_N_PAIRS = 8   # registered UNDER_CERTIFIED gate (frozen power-curve floor)
STUDY5_PRESETS = {
    "xl": {
        "roster_file": XL_ROSTER,
        "lang_label": "XL",
        "family": "XL — Cross-language invariance, external corpus "
                  "(single test, confirmatory; SEPARATE from Study-4 Family L)",
        "artefact": "hlang2_delta_v8xl",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md "
                            "(§3.1 H-LANG-2 Family XL; §2 selection protocol "
                            "+ certification gate as the admission rule; §6 "
                            "contract)",
        "registered_power": "power_study5.json::d_xl_hlang2_direction_power "
                            "(primary DGP = v7c-calibrated delta~0.245; "
                            "sensitivity DGP = v7 Python-arm delta~0.445; "
                            "reported at n=12/10/8; achieved-n lookup on the "
                            "frozen curve, no post-data simulation)",
        "matrix": RESULTS / "sms_track2_v8xl.json",
        "out": RESULTS / "hlang2_delta_v8xl.json",
    },
}


def load_xl_roster(roster_path: Path) -> tuple[tuple, dict]:
    """(grid, primary_map) from the frozen XL roster SSOT (§2 selection
    protocol output; frozen pre-mutant). primary_map is the roster's
    registered per-pair primary stratum (category->stratum map, data-
    independent), the XL analogue of PRIMARY_CELLS_V3."""
    roster = json.loads(Path(roster_path).read_text())
    pairs = roster["pairs"]
    for p in pairs:
        if "_" in p:
            raise ValueError(
                f"XL pair id {p!r} contains '_' — forbidden by the frozen "
                "cell-key convention (PAIR_MPk parses on the first '_'); "
                "use '.' or '-' inside pair ids, e.g. 'bisect.c'.")
    grid = tuple(sorted(p.lower() for p in pairs))
    primary_map = {p.lower(): int(v["primary_mp"]) for p, v in pairs.items()}
    return grid, primary_map


# --------------------------------------------------------------------------- #
# Byte-identical estimand + bootstrap, IMPORTED from the frozen H2-1' scorer.
# --------------------------------------------------------------------------- #
def _load_dualblind_module():
    spec = importlib.util.spec_from_file_location(
        "compute_dualblind_delta", ROOT / "scripts" / "compute_dualblind_delta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DBD = _load_dualblind_module()
cliffs_delta = _DBD.cliffs_delta                    # noqa: N816
boot_delta_distribution = _DBD.boot_delta_distribution
_is_excluded = _DBD._is_excluded
_parse_cell = _DBD._parse_cell
PRIMARY = _DBD.PRIMARY                              # PRIMARY_CELLS_V3 (v3b prohibited)


def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_sms(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def split_aligned_cross_c(sms: dict, grid: tuple = C_GRID_PUTS,
                          primary_map: dict | None = None) -> tuple[list, list]:
    """Split the C-port SMS pool into (aligned, cross) SMS lists over the grid
    PUTs (default: the 7-PUT Study-4 C grid). aligned = cells whose MP equals
    the PUT's registered primary MP; cross = all other adjudicated cells.
    Vacant cells excluded (§7b).

    Restricted to the grid so a pool that carries extra cells cannot leak a
    non-grid PUT into the estimand. Uses the SAME _is_excluded / PRIMARY as the
    Python H2-1' leg (imported), so the split is byte-identical. For the
    Family-XL external corpus, primary_map is the frozen roster's registered
    per-pair primary stratum (load_xl_roster); default None = PRIMARY_CELLS_V3."""
    primary = PRIMARY if primary_map is None else primary_map
    aligned, cross = [], []
    for cell, v in sms.items():
        put, mp = _parse_cell(cell)
        if put not in grid:
            continue
        if _is_excluded(v):
            continue
        (aligned if mp == primary[put] else cross).append(float(v["sms"]))
    return aligned, cross


def _c_puts_present(sms: dict, grid: tuple = C_GRID_PUTS) -> list:
    present = set()
    for cell in sms:
        put, _mp = _parse_cell(cell)
        if put in grid:
            present.add(put)
    return sorted(present)


# --------------------------------------------------------------------------- #
# H-LANG — cross-language invariance (Family L)
# --------------------------------------------------------------------------- #
def verdict_hlang(lower_95_one_sided: float, lang_label: str = "C") -> tuple[str, str]:
    """Registered decision rule (§3.3): lower bound > 0 -> CONFIRM."""
    if lower_95_one_sided > 0.0:
        return ("CONFIRM",
                f"the aligned>cross construct is LANGUAGE-INVARIANT: on the {lang_label} port "
                "the aligned slice dominates cross (delta_C one-sided 95% lower "
                "bound > 0), replicating the Python direction (NOETHER: MetaPatterns "
                "are operator-algebra invariants, not surface syntax)")
    return ("NOT_CONFIRMED",
            f"language-invariance does NOT replicate: the {lang_label}-port delta_C one-sided "
            "95% lower bound does not exceed 0 — reported as a genuine "
            "falsification of the language-invariance claim, not hedged away")


def analyze_hlang(sms_c: dict, B: int = B_BOOT, seed: int = MASTER_SEED,
                  grid: tuple = C_GRID_PUTS, lang_label: str = "C",
                  family: str = "L — Cross-language invariance (single test, "
                                "confirmatory)",
                  primary_map: dict | None = None) -> dict:
    aligned, cross = split_aligned_cross_c(sms_c, grid=grid,
                                           primary_map=primary_map)
    delta = cliffs_delta(aligned, cross)
    dist = boot_delta_distribution(aligned, cross, B=B, seed=seed)
    lower = float(np.quantile(dist, 0.05))              # one-sided 95% lower
    ci_lo = float(np.quantile(dist, 0.025))             # two-sided (descriptive)
    ci_hi = float(np.quantile(dist, 0.975))
    verdict, licensed = verdict_hlang(lower, lang_label=lang_label)
    return {
        "family": family,
        "statistic": f"two-sample Cliff's delta_C, aligned (j=k) vs cross (j!=k), "
                     f"on the {len(grid)} {lang_label} PUTs (PRIMARY_CELLS_V3 "
                     f"mapped to the {lang_label} cells)",
        "c_grid_puts": list(grid),
        "n_puts": len(_c_puts_present(sms_c, grid=grid)),
        "n_aligned": len(aligned),
        "n_cross": len(cross),
        "cliffs_delta_C": round(delta, 4),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "one_sided_95_lower_bound": round(lower, 4),
        "registered_test": "one-sided 95% percentile-bootstrap lower bound > 0 "
                           "(byte-identical bootstrap to H2-1')",
        "verdict": verdict,
        "verdict_bool": bool(lower > 0.0),
        "licensed_claim": licensed,
        "descriptive_only": {
            "two_sided_ci95": [round(ci_lo, 4), round(ci_hi, 4)],
            "note": "two-sided CI is EXPLORATORY (§3.3); the confirmatory verdict "
                    "is the one-sided lower bound > 0 direction test.",
        },
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(matrix_path=MATRIX, out_path=OUT, B: int = B_BOOT,
        seed: int = MASTER_SEED, preset: dict | None = None) -> dict:
    sms_c = load_sms(matrix_path)
    if preset is None:
        hlang = analyze_hlang(sms_c, B=B, seed=seed)
        report = {
            "artefact": "hlang_delta_v7c",
            "generated_by": "scripts/compute_hlang_delta.py",
            "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md "
                                "(§3.3 H-LANG; §7b contract; Amendment v1.1: n=7, v7c)",
            "integrity": "Pre-frozen before Study-4 C-port data generation; any "
                         "post-data modification must be disclosed as a deviation "
                         "(§5d, §8). Bootstrap byte-identical to H2-1'.",
            "inputs": {"c_port_sms_pool": _rel(matrix_path)},
            "master_seed": seed,
            "bootstrap_B": B,
            "primary_mp_rule": "PRIMARY_CELLS_V3 (A->MP1, B->MP2, C->MP5) mapped "
                               "cell-for-cell to the C cells; v3b prohibited",
            "registered_power": "0.6865 @ n=7 (v5 DGP, true delta 0.4385); below 0.80, "
                                "disclosed (power_study4.json::c...power_delta_gt0_at_n7)",
            "H_LANG_cross_language_invariance": hlang,
        }
    else:
        grid, primary_map = load_xl_roster(preset["roster_file"])
        hlang = analyze_hlang(sms_c, B=B, seed=seed, grid=grid,
                              lang_label=preset["lang_label"],
                              family=preset["family"],
                              primary_map=primary_map)
        # Registered XL certification/recruitment gate (§3.1): the frozen
        # power curve floors at n=8; below it no confirmatory verdict is
        # licensed. The gate value cannot be moved post-freeze.
        hlang["registered_min_n_pairs"] = XL_MIN_N_PAIRS
        if hlang["n_puts"] < XL_MIN_N_PAIRS:
            hlang["verdict"] = "UNDER_CERTIFIED"
            hlang["verdict_bool"] = False
            hlang["licensed_claim"] = (
                f"certification/recruitment gate: only {hlang['n_puts']} "
                f"certified program-language pairs are present (< registered "
                f"gate {XL_MIN_N_PAIRS}); delta_XL and its bound are reported "
                "factually; no confirmatory language-invariance verdict is "
                "licensed and no threshold is moved")
        report = {
            "artefact": preset["artefact"],
            "generated_by": "scripts/compute_hlang_delta.py (Study-5 additive "
                            "preset; Study-4 default path byte-unchanged)",
            "pre_registration": preset["pre_registration"],
            "integrity": "Pre-frozen before Study-5 data generation; any "
                         "post-data modification must be disclosed as a "
                         "deviation (PREREGISTRATION_STUDY5_v1.md §7, §8). "
                         "Bootstrap byte-identical to H2-1'/H-LANG.",
            "inputs": {"sms_pool": _rel(matrix_path),
                       "xl_roster": _rel(preset["roster_file"])},
            "master_seed": seed,
            "bootstrap_B": B,
            "primary_mp_rule": "frozen XL roster per-pair primary stratum "
                               "(configs/xl_roster.json; the registered "
                               "category->stratum map of "
                               "PREREGISTRATION_STUDY5_v1.md §2, data-"
                               "independent, frozen pre-mutant; v3b-style "
                               "selection on the response prohibited)",
            "registered_power": preset["registered_power"],
            "H_LANG_cross_language_invariance": hlang,
        }
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdict(report: dict) -> None:
    h = report["H_LANG_cross_language_invariance"]
    print("=== Study-4 H-LANG cross-language invariance verdict (Family L) ===")
    print(f"[H-LANG] delta_C={h['cliffs_delta_C']:+.4f} "
          f"one-sided 95% lower={h['one_sided_95_lower_bound']:+.4f} "
          f"(n_puts={h['n_puts']}, n_aligned={h['n_aligned']}, "
          f"n_cross={h['n_cross']})")
    print(f"    VERDICT: {h['verdict']} — {h['licensed_claim']}")
    print(f"    (descriptive) two-sided CI {h['descriptive_only']['two_sided_ci95']}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrix", default=None,
                    help="per-cell SMS pool SSOT (default: the Study-4 v7c pool, "
                         "or the preset's registered pool with --study5-family)")
    ap.add_argument("--out", default=None,
                    help="output SSOT path ('-' = stdout only, no file write; "
                         "default: the Study-4 v7c verdict path, or the preset's "
                         "registered path with --study5-family)")
    ap.add_argument("--study5-family", choices=sorted(STUDY5_PRESETS),
                    default=None,
                    help="Study-5 ADDITIVE preset (PREREGISTRATION_STUDY5_v1.md "
                         "§6): 'xl' = Family XL (H-LANG-2, cross-language "
                         "external corpus; grid + primary map read from the "
                         "frozen configs/xl_roster.json). Omitting this flag "
                         "reproduces the Study-4 H-LANG behaviour byte-identically.")
    args = ap.parse_args()
    preset = STUDY5_PRESETS[args.study5_family] if args.study5_family else None
    matrix = args.matrix or str(preset["matrix"] if preset else MATRIX)
    out = args.out or str(preset["out"] if preset else OUT)
    if preset and not Path(preset["roster_file"]).exists():
        print(f"ERROR: XL roster SSOT missing: {preset['roster_file']}\n"
              "The Family-XL roster is frozen by the §2 selection protocol in "
              "a dated pre-data amendment BEFORE any XL mutant generation. No "
              "roster exists at freeze time (PREREGISTRATION_STUDY5_v1.md "
              "§0.1).", file=sys.stderr)
        return 2
    if not Path(matrix).exists():
        if preset:
            print(f"ERROR: SMS pool SSOT missing: {matrix}\n"
                  "This script runs on the ANALYSIS leg, AFTER Study-5 SMS "
                  "scoring of the registered fresh pool. No Study-5 pool "
                  "exists at freeze time (PREREGISTRATION_STUDY5_v1.md §0.1).",
                  file=sys.stderr)
        else:
            print(f"ERROR: C-port SMS pool SSOT missing: {matrix}\n"
                  "This script runs on the ANALYSIS leg, AFTER Study-4 C-port SMS "
                  "scoring of the fresh v7c pool. No Study-4 C confirmatory data "
                  "exists yet at freeze time (registration §0.1, §0.3).",
                  file=sys.stderr)
        return 2
    out_path = None if out == "-" else out
    report = run(matrix, out_path, preset=preset)
    _print_verdict(report)
    if out_path is not None:
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
