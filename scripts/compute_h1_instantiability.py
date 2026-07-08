#!/usr/bin/env python3
"""Study-2 confirmatory analysis — H1' operator instantiability (RQ3 successor).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md before Study-2
data generation; any post-data modification must be disclosed as a deviation.

Implements EXACTLY the registered H1' test (PREREGISTRATION_STUDY2_v1.1.md §3
H1', §7b contract, supersedes v1.0 H2-5):

  Family E — H1' (RQ3 successor).  Per operator family (CE, OS, HP, TF, SI),
    count the confirmatory PUTs (of 28) on which the family produces >=5
    NON-EQUIVALENT admitted mutants.  Registered threshold: >=4 of 5 families
    clear >=8 of the 28 confirmatory PUTs (feasibility 0.843,
    power_study2_v11.json::h1_instantiability).  A deterministic count on the
    frozen pool, NOT a sampling test: SI (narrow high-risk family, Study-1 1/6)
    is expected to stay below the bar, so the criterion is a genuine test.

  Decision (§3 H1'):
    * >=4 of 5 families clear >=8/28  -> CONFIRM operator adequacy.
    * otherwise                       -> report achieved per-family counts
                                         factually (Study-1 honesty norm; no
                                         retroactive threshold move).

EXCLUSIONS (§2b, §2c).  The two calibration-pilot PUTs {a2, b4} and ALL
Study-1 pools are excluded: only the 28 registered confirmatory PUTs enter the
count.  A pilot PUT appearing in the input SSOT is dropped (and reported), never
counted.

INTEGRITY.  Pure function of the frozen admitted-pool SSOT (post V1-V4 + dedup +
CF/TF single-stratum filter) plus the registered constants below.  No tunable
knob outside the registration; no data peeking.  The operator family of each
admitted mutant is parsed from its pool filename with the SAME regex the
S5-audit / single-stratum filter uses (src/p2/mutators/stratum_filter.py), so
family attribution is byte-identical to the admission machinery.

Inputs (registration §7b):
  admitted-pool SSOT : data/results/sms_track2_v5.json  (150-cell matrix; each
                       cell carries an ``outcomes`` list of {file, label}; the
                       distinct files of a PUT ARE its admitted pool)
  equivalence ledger : OPTIONAL --ledger JSON {put: {file: {"equivalent": bool}}}
                       overriding the EQUIV labels derived from the matrix.
Output:
  data/results/h1_instantiability_v5.json

Usage:
    PYTHONPATH=src python3 scripts/compute_h1_instantiability.py
    PYTHONPATH=src python3 scripts/compute_h1_instantiability.py \
        --pool data/results/sms_track2_v5.json \
        --out  data/results/h1_instantiability_v5.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Family parse regex — the SAME pool-filename form the S5 audit and the CF/TF
# single-stratum admission filter use (src/p2/mutators/stratum_filter.py). Reuse
# guarantees the H1' family attribution matches the admission machinery exactly.
from p2.mutators.stratum_filter import _FNAME_CAT_RE as FNAME_CAT_RE  # noqa: E402

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY2_v1.1.md §2c, §3 H1') ------
MASTER_SEED = 20260708               # registration master seed (§7) — recorded
FAMILIES = ["CE", "OS", "HP", "TF", "SI"]   # the 5 operator families (§3 H1')
MIN_MUTANTS = 5                      # ">=5 non-equivalent mutants" per PUT (§3)
REG_M = 8                            # ">=M of 28 PUTs" (§3; largest M feasible >=0.80)
REG_X = 4                            # ">=X of 5 families" (§3)
REGISTERED_FEASIBILITY = 0.843       # power_study2_v11.json::h1_instantiability
PILOT_PUTS = frozenset({"a2", "b4"})        # calibration pilot (§2b), excluded
# Registered 28-PUT confirmatory roster (§2c; power_study2_v11.json coverage).
CONFIRMATORY_PUTS = [
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
]
# Outcome-independent coverage ceilings (blind-authored operator_registry.py;
# power_study2_v11.json::h1_instantiability.coverage_ceiling_confirmatory28). A
# family cannot instantiate on a PUT with no spec for it — hard upper bounds.
COVERAGE_CEILING = {"CE": 23, "OS": 14, "HP": 21, "TF": 15, "SI": 10}

POOL = RESULTS / "sms_track2_v5.json"
OUT = RESULTS / "h1_instantiability_v5.json"

EQUIV = "EQUIV"
_CELL_RE = re.compile(r"^([A-Da-d]\d+)_MP([1-5])$")


# --------------------------------------------------------------------------- #
# SSOT ingestion + validation
# --------------------------------------------------------------------------- #
def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_family(filename: str) -> str | None:
    """Operator family from a pool filename (SAME regex as the admission filter).

    e.g. ``m01_a1_CE1_claude_a02.py`` -> ``CE``. Returns None if unparseable.
    """
    m = FNAME_CAT_RE.match(Path(filename).name)
    return m.group(1) if m else None


def _validate_cell(key: str, cell) -> None:
    """Reject malformed input early (§ INTEGRITY: pure function of a valid SSOT)."""
    if not _CELL_RE.match(key):
        raise ValueError(f"malformed SMS cell key (expected '<PUT>_MP<k>'): {key!r}")
    if not isinstance(cell, dict) or "outcomes" not in cell:
        raise ValueError(f"cell {key!r} missing 'outcomes' list")
    for o in cell["outcomes"]:
        if not isinstance(o, dict) or "file" not in o or "label" not in o:
            raise ValueError(f"cell {key!r} has a malformed outcome entry: {o!r}")


def load_pool(path: str | Path) -> dict:
    matrix = json.loads(Path(path).read_text())
    for k, v in matrix.items():
        _validate_cell(k, v)
    return matrix


def _put_of(key: str) -> str:
    return key.split("_")[0].lower()


def per_put_pool(matrix: dict, ledger: dict | None = None) -> dict:
    """{put: {file: {"family": str|None, "equivalent": bool}}} over ALL PUTs.

    A file is the PUT's admitted mutant; it is EQUIVALENT iff labelled EQUIV in
    any cell (equivalence is MP-independent) or flagged in the optional ledger.
    Files that do not parse to a known family are retained with family=None and
    never counted toward any family bar.
    """
    pools: dict[str, dict] = {}
    for key, cell in matrix.items():
        put = _put_of(key)
        pool = pools.setdefault(put, {})
        for o in cell["outcomes"]:
            f = o["file"]
            rec = pool.setdefault(f, {"family": parse_family(f), "equivalent": False})
            if o["label"] == EQUIV:
                rec["equivalent"] = True
    if ledger:
        for put, files in ledger.items():
            p = pools.get(put.lower())
            if not p:
                continue
            for f, meta in files.items():
                if f in p and isinstance(meta, dict) and "equivalent" in meta:
                    p[f]["equivalent"] = bool(meta["equivalent"])
    return pools


# --------------------------------------------------------------------------- #
# H1' — per-family x per-PUT non-equivalent counts + verdict
# --------------------------------------------------------------------------- #
def family_put_counts(pools: dict) -> dict:
    """{put: {family: n_nonequivalent}} restricted to the 28 confirmatory PUTs.

    Pilot PUTs {a2, b4} and any non-confirmatory (incl. Study-1) PUT are dropped.
    """
    counts: dict[str, dict] = {}
    for put in CONFIRMATORY_PUTS:
        fam_ct = {fam: 0 for fam in FAMILIES}
        for _f, rec in pools.get(put, {}).items():
            fam = rec["family"]
            if rec["equivalent"] or fam not in fam_ct:
                continue
            fam_ct[fam] += 1
        counts[put] = fam_ct
    return counts


def verdict_h1(n_families_clearing: int) -> tuple[str, str]:
    """Registered decision rule (§3 H1'): >=4 of 5 families clear >=8/28."""
    if n_families_clearing >= REG_X:
        return ("CONFIRM",
                f"operators adequately instantiate on the confirmatory grid "
                f"(>={REG_X}/5 families produce >={MIN_MUTANTS} non-equivalent "
                f"mutants on >={REG_M}/28 PUTs)")
    return ("NOT_CONFIRMED",
            "operator instantiability below the registered bar; achieved "
            "per-family counts reported factually (no threshold move)")


def analyze_h1(matrix: dict, ledger: dict | None = None) -> dict:
    pools = per_put_pool(matrix, ledger)
    counts = family_put_counts(pools)

    present = [p for p in CONFIRMATORY_PUTS if p in pools]
    missing = [p for p in CONFIRMATORY_PUTS if p not in pools]
    pilots_seen = sorted(p for p in PILOT_PUTS if p in pools)
    study1_or_other = sorted(
        p for p in pools
        if p not in CONFIRMATORY_PUTS and p not in PILOT_PUTS)

    per_family = {}
    for fam in FAMILIES:
        cleared = [p for p in CONFIRMATORY_PUTS if counts[p][fam] >= MIN_MUTANTS]
        per_family[fam] = {
            "coverage_ceiling_28": COVERAGE_CEILING[fam],
            "puts_cleared": len(cleared),
            "cleared_put_ids": cleared,
            "clears_bar": len(cleared) >= REG_M,
            "per_put_nonequiv_count": {p: counts[p][fam] for p in CONFIRMATORY_PUTS},
        }
    n_clearing = sum(1 for fam in FAMILIES if per_family[fam]["clears_bar"])
    verdict, licensed = verdict_h1(n_clearing)

    return {
        "family": "E — Operator instantiability (deterministic count, verdict-factual)",
        "statistic": "per family, # of 28 confirmatory PUTs with >=5 "
                     "non-equivalent admitted mutants",
        "registered_threshold": {
            "min_mutants_per_put": MIN_MUTANTS, "M_puts": REG_M,
            "X_families": REG_X,
            "shape": ">=4 of 5 families clear >=8 of 28 confirmatory PUTs",
            "feasibility": REGISTERED_FEASIBILITY,
        },
        "n_confirmatory_puts_expected": len(CONFIRMATORY_PUTS),
        "n_confirmatory_puts_present": len(present),
        "confirmatory_puts_missing_from_pool": missing,
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "pilot_puts_seen_and_dropped": pilots_seen,
        "non_confirmatory_puts_dropped": study1_or_other,
        "per_family": per_family,
        "n_families_clearing_bar": n_clearing,
        "verdict": verdict,
        "licensed_claim": licensed,
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(pool_path=POOL, out_path=OUT, ledger_path=None) -> dict:
    matrix = load_pool(pool_path)
    ledger = json.loads(Path(ledger_path).read_text()) if ledger_path else None
    report = {
        "artefact": "h1_instantiability_v5",
        "generated_by": "scripts/compute_h1_instantiability.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md "
                            "(§3 H1'; §2b/§2c pilot exclusion; §7b contract)",
        "integrity": "Pre-frozen before Study-2 data generation; any post-data "
                     "modification must be disclosed as a deviation.",
        "inputs": {
            "admitted_pool_sms": _rel(pool_path),
            "equivalence_ledger": _rel(ledger_path) if ledger_path else None,
        },
        "master_seed": MASTER_SEED,
        "H1_operator_instantiability": analyze_h1(matrix, ledger),
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    h1 = report["H1_operator_instantiability"]
    print("=== Study-2 H1' operator-instantiability verdict (confirmatory) ===")
    print(f"confirmatory PUTs present: {h1['n_confirmatory_puts_present']}/"
          f"{h1['n_confirmatory_puts_expected']}  "
          f"(pilots dropped: {h1['pilot_puts_seen_and_dropped']})")
    for fam in FAMILIES:
        f = h1["per_family"][fam]
        print(f"    {fam}: {f['puts_cleared']:2d}/28 PUTs cleared "
              f"(bar {REG_M}; ceiling {f['coverage_ceiling_28']}) -> "
              f"{'CLEARS' if f['clears_bar'] else 'below bar'}")
    print(f"families clearing >={REG_M}/28: {h1['n_families_clearing_bar']}/5 "
          f"(bar >={REG_X})")
    print(f"    VERDICT: {h1['verdict']} — {h1['licensed_claim']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", default=str(POOL),
                    help="admitted-pool SMS SSOT (150-cell matrix)")
    ap.add_argument("--ledger", default=None,
                    help="optional equivalence/dedup ledger JSON")
    ap.add_argument("--out", default=str(OUT), help="output SSOT path")
    args = ap.parse_args()
    if not Path(args.pool).exists():
        print(f"ERROR: admitted-pool SSOT missing: {args.pool}\n"
              "This script runs on the ANALYSIS leg, after Study-2 pool "
              "construction (CAMPAIGN_RUNBOOK.md §2.3-§2.4). No Study-2 data "
              "exists yet at freeze time.", file=sys.stderr)
        return 2
    report = run(args.pool, args.out, args.ledger)
    _print_verdicts(report)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
