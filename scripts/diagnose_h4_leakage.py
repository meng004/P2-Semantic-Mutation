#!/usr/bin/env python3
"""H4' leakage decomposition — POST-HOC, EXPLORATORY diagnosis (Phase-1 diagnostician).

INTEGRITY / SCOPE
-----------------
The registered H4' verdict (data/results/s5_purity_v5.json) is NOT_CONFIRMED
(mean suspect_share 0.1714 > 0.05) and is FROZEN. This script changes NOTHING
about that verdict. It is a purely offline, deterministic, clearly-labelled
POST-HOC diagnosis that decomposes the 117 confirmatory multi-stratum mutants
into two buckets:

  (A) MEASUREMENT-CONTEXT ARTIFACT — the multi-stratum status is an artifact of
      HOW/WHERE the flip count was measured (which families the admission filter
      actually screened, and the single-shot repeats=1 audit vs repeats=20
      admission majority vote).
  (B) CONSTRUCT-LEVEL PHENOMENON — the double-flip is REAL and reproducible under
      the stronger admission measurement (repeats=20): a single-edit semantic
      fault on a richer PUT genuinely perturbs >= 2 behavioural invariants.

No threshold is re-litigated; no number is asserted that this script did not
compute from committed artefacts.

INPUTS (all committed / immutable):
  data/results/sms_track2_v5.json   frozen Study-2 per-cell SMS matrix (repeats=1)
  data/results/s5_purity_v5.json    frozen H4' verdict SSOT
  data/results/s5_purity_v4.json    Study-1 S5 audit (repeats=20) for reconciliation
  data/mutants/{put}_pool_v5/       committed mutant pools (post-"admission")
  src/p2/mutators/stratum_filter.py  the admission filter under test

OUTPUT:
  data/results/h4_leakage_diagnosis_v5.json

Usage:
  PYTHONPATH=src python3 scripts/diagnose_h4_leakage.py
  PYTHONPATH=src python3 scripts/diagnose_h4_leakage.py --limit 3   # smoke
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.stratum_filter import (  # noqa: E402
    audit_matrix, category_from_filename,
    evaluate_mutant_labels, classify_flips, CONSTRAINED_CATEGORIES, KILLED,
)

# --- FROZEN historical parser (incident P8) -------------------------------- #
# This diagnosis documents the EXACT pre-remediation behaviour of
# ``category_from_op_id``: the anchor ``...\d+$`` rejected the cross-source
# suffix and returned None, silently disabling the v5 CF/TF screen. The library
# parser has since been fixed (P8 remediation, 2026-07-09) to tolerate the
# suffix, so importing it here would no longer reproduce the committed no-op
# evidence. We pin the buggy regex locally so this post-hoc SSOT
# (h4_leakage_diagnosis_v5.json) stays byte-reproducible; the fix is
# forward-looking and does not alter this frozen artefact.
_OPID_CAT_RE_V5_BUGGY = re.compile(r"^[a-d][1-8]_([A-Z]{2})\d+$")


def category_from_op_id(op_id: str):
    """P8-historical parser: reproduces the null returned for v5-suffixed ids."""
    m = _OPID_CAT_RE_V5_BUGGY.match(op_id)
    return m.group(1) if m else None

RESULTS = ROOT / "data" / "results"
MUTANTS = ROOT / "data" / "mutants"
MATRIX = RESULTS / "sms_track2_v5.json"
V5_PURITY = RESULTS / "s5_purity_v5.json"
V4_PURITY = RESULTS / "s5_purity_v4.json"
OUT = RESULTS / "h4_leakage_diagnosis_v5.json"

MULTISTRATUM_MIN_FLIP = 2
ADMISSION_REPEATS = 20   # what the filter uses (make_screen_fn(repeats=20))
AUDIT_REPEATS = 1        # what the frozen v5 matrix used (verified per-cell)

# PUT-class semantics (first letter of the PUT id). Derived from the PUT module
# docstrings (src/p2/puts/*.py), NOT invented.
PUT_CLASS = {
    "a": "classical-numerics (ODE / interpolation / quadrature)",
    "b": "stochastic-simulation (MCMC / rejection / Monte-Carlo)",
    "c": "surrogate-regression (GaussianProcess / SVR / kernel)",
    "d": "ML-classifier (MLP / LDA / GP-classifier, fit-data heavy)",
}


def put_class_of(put: str) -> str:
    return put[0].lower()


def op_id_from_filename(fname: str) -> str:
    """Reconstruct the build-time op_id the screen received.

    Pool file  m19_c7_TF1_claude_a03.py  came from cache file
    c7_TF1_claude_attempt03.py; pool_builder set op_id = name-before-'_attempt'
    = 'c7_TF1_claude' (INCLUDING the model-source suffix). We reproduce that
    exact string to show what category_from_op_id actually returned at build.
    """
    stem = Path(fname).stem            # m19_c7_TF1_claude_a03
    parts = stem.split("_")            # [m19, c7, TF1, claude, a03]
    # drop leading rank token (m19) and trailing attempt token (a03)
    core = parts[1:-1]                 # [c7, TF1, claude]
    return "_".join(core)


# --------------------------------------------------------------------------- #
# 1. audit side (free) — read the frozen repeats=1 matrix
# --------------------------------------------------------------------------- #
def load_audit(matrix: dict) -> dict:
    puts = sorted({k.split("_")[0] for k in matrix})
    audit = audit_matrix(matrix, puts)
    # (put, file) -> record
    per = {}
    for m in audit["per_mutant"]:
        per[(m["put"], m["file"])] = m
    # confirm all cells are repeats=1
    reps = collections.Counter(c.get("repeats") for c in matrix.values())
    return {"per": per, "audit_repeats_hist": dict(reps),
            "n_mutants": audit["n_mutants"], "n_multistratum": audit["n_multistratum"]}


# --------------------------------------------------------------------------- #
# 2. admission side (heavy) — re-run repeats=20 singleton on the flagged mutants
# --------------------------------------------------------------------------- #
def rerun_admission(put: str, fname: str, repeats: int = ADMISSION_REPEATS) -> dict:
    path = MUTANTS / f"{put.lower()}_pool_v5" / fname
    labels = evaluate_mutant_labels(put.lower(), path, repeats=repeats)
    n, flipped = classify_flips(labels)
    return {"labels": {int(k): v for k, v in labels.items()},
            "flip_count": n, "flipped_invariants": flipped}


# --------------------------------------------------------------------------- #
# 3. counterfactual suspect_share from the frozen matrix
# --------------------------------------------------------------------------- #
def suspect_share_mean(matrix: dict, reject: set) -> tuple[float, int]:
    """Mean suspect_share over 140 cells, treating (put,file) in `reject` as
    if never admitted (removed from both numerator and denominator).

    `reject` is a set of (PUT_upper, file). Multi-stratum flag uses the frozen
    audit flip counts (the audit's exact context)."""
    puts = sorted({k.split("_")[0] for k in matrix})
    audit = audit_matrix(matrix, puts)
    flips = {(m["put"], m["file"]): m["flip_count"] for m in audit["per_mutant"]}
    shares = []
    for put in puts:
        for mp in range(1, 6):
            cell = matrix.get(f"{put}_MP{mp}")
            if cell is None:
                continue
            killed = [o["file"] for o in cell["outcomes"]
                      if o["label"] == KILLED and (put, o["file"]) not in reject]
            suspect = [f for f in killed
                       if flips.get((put, f), 0) >= MULTISTRATUM_MIN_FLIP]
            shares.append((len(suspect) / len(killed)) if killed else 0.0)
    mean = sum(shares) / len(shares) if shares else 0.0
    return round(mean, 4), len(shares)


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="cap admission re-runs (smoke test); 0 = all 117")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    matrix = json.loads(MATRIX.read_text())
    v5 = json.loads(V5_PURITY.read_text())
    v4 = json.loads(V4_PURITY.read_text())

    audit = load_audit(matrix)
    per = audit["per"]

    # ---- the 117 confirmatory multi-stratum mutants (from the frozen audit) --
    ms = [m for m in per.values() if m["flip_count"] >= MULTISTRATUM_MIN_FLIP]
    ms.sort(key=lambda m: (m["put"], m["file"]))
    if args.limit:
        ms = ms[: args.limit]

    print(f"[diag] {len(ms)} multi-stratum mutants to re-screen "
          f"(admission repeats={ADMISSION_REPEATS}, singleton)")

    per_mutant = []
    t0 = time.time()
    for i, m in enumerate(ms, 1):
        put, fname, fam = m["put"], m["file"], m["category"]
        audit_flips = m["flipped_invariants"]
        adm = rerun_admission(put, fname)
        agree = (adm["flipped_invariants"] == audit_flips)
        still_multi = adm["flip_count"] >= MULTISTRATUM_MIN_FLIP
        opid = op_id_from_filename(fname)
        screened_family = fam in CONSTRAINED_CATEGORIES
        # A vs B classification:
        #   B (construct)     : real double-flip under the strong measurement.
        #   A (measurement)   : audit repeats=1 over-detected; admission single.
        bucket = "B_construct" if still_multi else "A_measurement"
        per_mutant.append({
            "put": put, "put_class": put_class_of(put),
            "put_class_name": PUT_CLASS.get(put_class_of(put), "?"),
            "file": fname, "family": fam,
            "build_op_id": opid,
            "category_from_op_id": category_from_op_id(opid),
            "screened_family_by_design": screened_family,
            "audit_flips_repeats1": audit_flips,
            "admission_flips_repeats20": adm["flipped_invariants"],
            "admission_labels": adm["labels"],
            "agree": agree,
            "still_multistratum_under_admission": still_multi,
            "bucket": bucket,
            "co_flip_pair": tuple(audit_flips),
        })
        if i % 10 == 0 or i == len(ms):
            print(f"  {i}/{len(ms)}  {put} {fname}  audit={audit_flips} "
                  f"adm20={adm['flipped_invariants']} -> {bucket} "
                  f"({round(time.time()-t0)}s)")

    # ------------------------------------------------------------------ #
    # aggregates
    # ------------------------------------------------------------------ #
    n_B = sum(1 for r in per_mutant if r["bucket"] == "B_construct")
    n_A = sum(1 for r in per_mutant if r["bucket"] == "A_measurement")

    # filter-coverage decomposition (why each was in the pool at all)
    cov = collections.Counter()
    for r in per_mutant:
        if not r["screened_family_by_design"]:
            cov["OS/SI unscreened-family-by-design"] += 1
        elif r["category_from_op_id"] is None:
            cov["CF/TF screen-was-noop (op_id regex rejected source-suffix)"] += 1
        else:
            cov["CF/TF screened-but-admitted"] += 1

    by_family = collections.Counter(r["family"] for r in per_mutant)
    by_family_bucket = collections.defaultdict(collections.Counter)
    for r in per_mutant:
        by_family_bucket[r["family"]][r["bucket"]] += 1

    # per-class x family x co-flip pair fingerprint (v5)
    fp_v5 = collections.defaultdict(collections.Counter)
    for r in per_mutant:
        fp_v5[(r["put_class"], r["family"])][str(list(r["co_flip_pair"]))] += 1
    fp_v5_out = {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(fp_v5.items())}

    # Study-1 v4 fingerprint (repeats=20 audit) for reconciliation
    fp_v4 = collections.defaultdict(collections.Counter)
    v4_by_fam = collections.Counter()
    v4_ms_by_fam = collections.Counter()
    for mm in v4["per_mutant"]:
        fam = category_from_filename(mm.get("file", ""))
        v4_by_fam[fam] += 1
        if mm["flip_count"] >= 2:
            v4_ms_by_fam[fam] += 1
            cls = mm["put"][0].lower()
            fp_v4[(cls, fam)][str(mm["flipped_invariants"])] += 1
    fp_v4_out = {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(fp_v4.items())}

    # ------------------------------------------------------------------ #
    # counterfactuals (post-hoc, NOT a re-verdict)
    # ------------------------------------------------------------------ #
    # CF-1: screen applied to ALL FIVE families in the AUDIT's exact context
    #       (repeats=1 pool) -> reject every audit-flip>=2 mutant.
    reject_audit_ctx = {(m["put"], m["file"]) for m in ms} if not args.limit else \
        {(m["put"], m["file"]) for m in per.values() if m["flip_count"] >= 2}
    cf1_mean, cf1_cells = suspect_share_mean(matrix, reject_audit_ctx)

    # CF-2: screen applied to all families in the ADMISSION context (repeats=20).
    #       Only the B (real) mutants are rejected; the A mutants pass admission
    #       yet are STILL counted multi-stratum by the frozen repeats=1 audit ->
    #       the residual leakage is exactly the measurement-context mismatch.
    reject_adm_ctx = {(r["put"], r["file"]) for r in per_mutant
                      if r["bucket"] == "B_construct"}
    cf2_mean, _ = suspect_share_mean(matrix, reject_adm_ctx)

    report = {
        "artefact": "h4_leakage_diagnosis_v5",
        "status": "POST-HOC / EXPLORATORY — the registered H4' verdict "
                  "(NOT_CONFIRMED, mean suspect_share 0.1714) is FROZEN and "
                  "UNCHANGED by this analysis. No threshold is re-litigated.",
        "generated_by": "scripts/diagnose_h4_leakage.py",
        "measurement_contexts": {
            "audit_frozen_v5": {"repeats": AUDIT_REPEATS, "context": "full-pool",
                                "source": "data/results/sms_track2_v5.json",
                                "verified_repeats_hist": audit["audit_repeats_hist"]},
            "admission_filter": {"repeats": ADMISSION_REPEATS,
                                 "context": "singleton tempdir",
                                 "source": "p2.mutators.stratum_filter.make_screen_fn(20)"},
            "study1_v4_audit": {"repeats": 20,
                                "source": "data/results/s5_purity_v4.json"},
        },
        "root_cause_mechanical": {
            "finding": "The CF/TF single-stratum admission filter was a SILENT "
                       "NO-OP for the entire cross-source (v5) campaign.",
            "why": "pool_builder set op_id = filename-before-'_attempt' = e.g. "
                   "'c7_TF1_claude' (INCLUDING the model-source suffix). "
                   "stratum_filter._OPID_CAT_RE = '^[a-d][1-8]_([A-Z]{2})\\\\d+$' "
                   "requires end-of-string after the operator digit, so the "
                   "'_claude'/'_deepseek'/'_gpt' suffix makes category_from_op_id "
                   "return None -> screen_mutant treats it as an UNCONSTRAINED "
                   "category and admits WITHOUT evaluation. Study-1 op_ids had no "
                   "source suffix, so the same regex worked there.",
            "evidence": "every CF/TF multi-stratum mutant below has "
                        "category_from_op_id(build_op_id) == null.",
            "secondary": "OS/SI were never in CONSTRAINED_CATEGORIES {CF,TF}, so "
                         "the screen never targeted them by design.",
        },
        "A_vs_B_decomposition": {
            "definition": {
                "A_measurement": "multi-stratum under the frozen repeats=1 audit "
                                 "but SINGLE-stratum (flip<=1) under the repeats=20 "
                                 "admission majority vote -> a measurement-context "
                                 "artifact of single-shot scoring.",
                "B_construct": "multi-stratum under BOTH measurements (real, "
                               "reproducible multi-invariant perturbation).",
            },
            "n_total_multistratum": len(per_mutant),
            "n_A_measurement": n_A,
            "n_B_construct": n_B,
            "by_family": dict(by_family),
            "by_family_bucket": {k: dict(v) for k, v in by_family_bucket.items()},
            "filter_coverage_breakdown": dict(cov),
        },
        "counterfactuals_posthoc": {
            "CF1_audit_context_all_families": {
                "description": "IF the screen had been correctly wired AND extended "
                               "to all 5 families AND applied in the audit's exact "
                               "context (repeats=1), every audit-flip>=2 mutant is "
                               "rejected at admission.",
                "n_rejected_of_117": len(reject_audit_ctx),
                "fraction_rejected": round(len(reject_audit_ctx) / max(1, len(ms)), 4)
                                     if args.limit == 0 else None,
                "counterfactual_mean_suspect_share": cf1_mean,
                "n_cells": cf1_cells,
                "note": "NOT a re-verdict; a mechanical 'what-if' on the frozen matrix.",
            },
            "CF2_admission_context_all_families": {
                "description": "IF the screen were applied in the ADMISSION context "
                               "(repeats=20) to all families, only the B (real) "
                               "mutants are rejected; the A mutants pass admission "
                               "but the frozen repeats=1 audit still counts them.",
                "n_rejected_B": len(reject_adm_ctx),
                "residual_mean_suspect_share": cf2_mean,
                "note": "residual > 0 isolates the repeats=1-vs-20 measurement gap.",
            },
        },
        "fingerprints": {
            "v5_class_family_coflip": fp_v5_out,
            "v4_class_family_coflip": fp_v4_out,
            "v4_multistratum_by_family": dict(v4_ms_by_fam),
            "v4_total_by_family": dict(v4_by_fam),
            "put_class_legend": PUT_CLASS,
        },
        "registered_verdict_unchanged": {
            "verdict": v5["H4_attribution_purity"]["verdict"],
            "mean_suspect_share": v5["H4_attribution_purity"]["mean_suspect_share"],
            "per_family_multistratum": v5["H4_attribution_purity"]["per_family_multistratum"],
        },
        "per_mutant": per_mutant,
    }

    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[diag] A(measurement)={n_A}  B(construct)={n_B}  of {len(per_mutant)}")
    print(f"[diag] coverage: {dict(cov)}")
    print(f"[diag] CF1 counterfactual mean suspect_share = {cf1_mean} "
          f"(rejected {len(reject_audit_ctx)})")
    print(f"[diag] CF2 residual mean suspect_share = {cf2_mean}")
    print(f"[diag] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
