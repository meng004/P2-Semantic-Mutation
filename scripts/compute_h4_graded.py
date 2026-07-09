#!/usr/bin/env python3
"""Study-3 confirmatory analysis — H4''-graded + H4''-strict (RQ-S3).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY3_v2.md (§3, §7b contract)
BEFORE any Study-3 data generation. Any post-data modification of this script
MUST be disclosed as a deviation in the registration §10 appendix.

    ┌─────────────────────────────────────────────────────────────────────┐
    │ PRE-FROZEN SCORER — no Study-3 mutant, SMS cell, or attribution      │
    │ outcome existed when this file was frozen. The two decision rules    │
    │ below are the registered a-priori rules; changing a threshold or an  │
    │ estimand after any confirmatory outcome is visible is a protocol     │
    │ violation (registration §5c, §8).                                    │
    └─────────────────────────────────────────────────────────────────────┘

Implements EXACTLY the two registered Family-G attribution verdicts
(PREREGISTRATION_STUDY3_v2.md §3.1, §3.2, §7b):

  H4''-graded (§3.1, PRIMARY).  On the structurally-rich PUT classes (C, D) a
    single semantic fault perturbs several invariant strata at once, so a
    single-valued purity bar fails by construction. Instead score, per DETECTED
    mutant m (flip count >= 1) declared to its class-primary MetaPattern m*:

        s_m = 𝟙[m* ∈ flipset(m)] / |flipset(m)|              (a ratio in [0,1])

    Cell/PUT statistic = mean s_m over the detected mutants declared to a PUT.
    Rich aggregate     = mean over the rich-class (C, D) PUTs.
    Test               = one-sided 95% percentile-bootstrap lower bound on the
                         rich aggregate (B=10,000, seed 20260708).
    Decision (FROZEN)  = CONFIRM iff boot_lower_95 > 0.15.
    Power 0.82 at n_rich = 15 (power_study3.json::a…tau_0.15[15]); the τ=0.10
    floor reaches 0.92. τ=0.20 is NOT powered and is NOT a registered bar.

  H4''-strict (§3.2, SUB-HYPOTHESIS).  Where coupling is absent (CE, HP: both
    0-leakage) or stable/screenable (CF: admitted THROUGH the fixed all-family
    screen, its double-flips rejected at admission), the single-stratum purity
    premise is tested:

        purity = (detected clean-family mutants with flip == 1) / (detected
                  clean-family {CE, HP, CF-with-screen} mutants)
        Test   = one-sided 95% lower Clopper-Pearson bound on purity.
    Decision (FROZEN) = CONFIRM iff cp_lower_95 >= 0.90 AND the wired all-family
                        screen matched > 0 candidates. A zero-candidate screen
                        is the incident-P8 silent no-op and forces a loud FAIL
                        verdict (registration §5c screen-smoke gate), never a
                        silent pass.

FLIP MACHINERY IS IDENTICAL TO S5 / STUDY-2.  The per-mutant invariant-flip
classification is NOT reimplemented here: it is imported from
``p2.mutators.stratum_filter.audit_matrix(..., constrained=ALL_FAMILIES)`` — the
SAME offline invariant-flip definition (a mutant perturbs invariant k iff KILLED
under MP_k) used by the Study-1 S5 audit and the fixed all-family admission
screen. No measurement change is introduced pre- or post-data.

Primary-MP rule: PRIMARY_CELLS_V3 (P2_PRIMARY_VERSION=v3; the v3b
selection-on-response path is prohibited, §4a). A→MP1, B→MP2, C→MP5, D→MP2.

EXCLUSIONS (§2b, §2c, §7). Pilot PUTs {a2, b4} are excluded from every
confirmatory statistic; silent (flip == 0) mutants are undetected and excluded
from the graded share (no 0/0); vacant cells are excluded.

Multiplicity (§7): Family G holds the two attribution tests; Holm(2) within G
controls the family. Both tests are one-sided at α = 0.05. The frozen per-
hypothesis decision rules above are reported; the Holm(2) family control is
recorded in the output for transparency.

Inputs (registration §7b):
  per-cell SMS matrix : data/results/sms_track2_v6.json  (fresh validated pool;
                        each cell's ``outcomes`` list of {file, label})
Output:
  data/results/h4_graded_v6.json  (both verdicts + licensed strings)

Usage:
    PYTHONPATH=src python3 scripts/compute_h4_graded.py
    PYTHONPATH=src python3 scripts/compute_h4_graded.py \
        --matrix data/results/sms_track2_v6.json \
        --out    data/results/h4_graded_v6.json
    # smoke against the PILOT output (NOT a confirmatory run):
    PYTHONPATH=src python3 scripts/compute_h4_graded.py \
        --matrix data/results/sms_track2_v6_pilot.json --pilot-smoke --out -
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Flip / audit machinery — IMPORTED, never reimplemented (§7b, identical to S5).
from p2.mutators.stratum_filter import (  # noqa: E402
    audit_matrix, category_from_filename, ALL_FAMILIES, KILLED,
)
from p2.config.primary import PRIMARY_CELLS_V3  # noqa: E402

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY3_v2.md §3, §7) -------------
MASTER_SEED = 20260708                 # bootstrap seed (§7 "all bootstrap at 20260708")
N_BOOT = 10000                         # graded percentile-bootstrap resamples (§3.1)
ALPHA = 0.05                           # one-sided (§3.1, §3.2)
GRADED_THRESHOLD = 0.15                # rich-class mean primary-stratum share bar (§3.1)
STRICT_THRESHOLD = 0.90               # single-stratum purity bar (§3.2)
POOLED_GATE = 24                       # Study-4 §3.2 recruitment gate (pooled n_rich)
RICH_CLASSES = ("c", "d")              # surrogate-regression + ML-classifier (§3.1)
CLEAN_FAMILIES = ("CE", "HP", "CF")    # 0-leakage + stable/screenable (§3.2)
PILOT_PUTS = frozenset({"a2", "b4"})   # calibration pilot (§2b) — excluded
CONFIRMATORY_PUTS = [                   # 28-PUT roster (§2c), pilots removed
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
]

MATRIX = RESULTS / "sms_track2_v6.json"
OUT = RESULTS / "h4_graded_v6.json"
POOLED_OUT = RESULTS / "h4_graded_v7.json"   # Study-4 pooled two-arm output (§7b)

_CELL_RE = re.compile(r"^([A-Da-d]\d+)_MP([1-5])$")


# --------------------------------------------------------------------------- #
# SSOT ingestion + validation
# --------------------------------------------------------------------------- #
def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _validate_cell(key: str, cell) -> None:
    if not _CELL_RE.match(key):
        raise ValueError(f"malformed SMS cell key (expected '<PUT>_MP<k>'): {key!r}")
    if not isinstance(cell, dict) or "outcomes" not in cell:
        raise ValueError(f"cell {key!r} missing 'outcomes' list")
    for o in cell["outcomes"]:
        if not isinstance(o, dict) or "file" not in o or "label" not in o:
            raise ValueError(f"cell {key!r} has a malformed outcome entry: {o!r}")


def load_matrix(path: str | Path) -> dict:
    matrix = json.loads(Path(path).read_text())
    for k, v in matrix.items():
        _validate_cell(k, v)
    return matrix


def _confirmatory_puts_present(matrix: dict) -> list:
    """Uppercase confirmatory PUT ids present in the matrix (pilots excluded)."""
    present = {k.split("_MP")[0].lower() for k in matrix}
    return [p.upper() for p in CONFIRMATORY_PUTS if p in present]


def _puts_present(matrix: dict, pilot_smoke: bool = False) -> list:
    """PUT set the analysis runs over. Confirmatory: the 28-PUT roster (pilots
    excluded, §2c). Pilot-smoke: whatever PUTs the pilot matrix carries (so the
    scorer exercises real pipeline output end-to-end on {a2,b4}); firewalled and
    clearly labelled, never a confirmatory verdict (§2b)."""
    if pilot_smoke:
        present = sorted({k.split("_MP")[0].upper() for k in matrix})
        return present
    return _confirmatory_puts_present(matrix)


# --------------------------------------------------------------------------- #
# bootstrap / Clopper-Pearson bounds (registered)
# --------------------------------------------------------------------------- #
def boot_lower_95(pool, n_boot=N_BOOT, seed=MASTER_SEED, alpha=ALPHA) -> float:
    """One-sided 95% percentile-bootstrap lower bound on the mean of ``pool``.

    B=10,000, seed 20260708 (registration §3.1, §7). Byte-identical resampling
    scheme to power_analysis_study3._boot_lower_pool (the calibrated anchor)."""
    pool = np.asarray(pool, dtype=float)
    if pool.size == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    boot = rng.choice(pool, size=(n_boot, pool.size), replace=True).mean(axis=1)
    return float(np.quantile(boot, alpha))


def lower_cp(k: int, n: int, alpha=ALPHA) -> float:
    """One-sided lower Clopper-Pearson bound on a binomial proportion (§3.2).

    Uses the exact Beta quantile; the k == n edge case reduces to alpha**(1/n).
    Identical to power_analysis_study3.power_strict.lower_cp."""
    if n == 0:
        return 0.0
    if k >= n:
        return alpha ** (1.0 / n)
    from scipy import stats as sps
    return float(sps.beta.ppf(alpha, k, n - k + 1))


# --------------------------------------------------------------------------- #
# per-mutant flip map via the IMPORTED all-family audit
# --------------------------------------------------------------------------- #
def flip_map(matrix: dict, puts_upper: list) -> dict:
    """{(put, file): (flip_count, flipped_invariants, category)} via audit_matrix.

    Delegates entirely to p2.mutators.stratum_filter.audit_matrix with the
    all-family scope (§7b); no local reimplementation of the flip classifier.
    ``n_screened_candidates`` (in-scope mutant count, all-family) is the basis of
    the registered screen-smoke gate."""
    audit = audit_matrix(matrix, puts_upper, constrained=ALL_FAMILIES)
    per = {(m["put"], m["file"]): (m["flip_count"], m["flipped_invariants"],
                                   m["category"])
           for m in audit["per_mutant"]}
    return per, audit


# --------------------------------------------------------------------------- #
# H4''-graded (§3.1)
# --------------------------------------------------------------------------- #
def analyze_graded(matrix: dict, per_mutant: dict, exclude_pilots: bool = True) -> dict:
    """Rich-class (C, D) mean primary-stratum kill share + bootstrap lower bound."""
    # detected mutants per PUT -> s_m; unique per (put, file) to avoid recounting
    # a mutant that appears in all 5 MP cells.
    per_put_shares: dict = {}
    per_put_detail: dict = {}
    for (put, fname), (fc, fl, cat) in per_mutant.items():
        put_l = put.lower()
        if exclude_pilots and put_l in PILOT_PUTS:  # §2b firewall
            continue
        if fc < 1:                                 # silent -> undetected (no 0/0)
            continue
        primary = PRIMARY_CELLS_V3[put_l]
        s_m = (1.0 if primary in fl else 0.0) / fc
        per_put_shares.setdefault(put, []).append(s_m)
        per_put_detail.setdefault(put, []).append(
            {"file": fname, "category": cat, "flip_count": fc,
             "flipped_invariants": fl, "primary_mp": primary,
             "s_m": round(s_m, 4)})

    per_put_mean = {p: round(float(np.mean(v)), 4)
                    for p, v in sorted(per_put_shares.items())}

    rich_put_means = [np.mean(v) for p, v in per_put_shares.items()
                      if p[0].lower() in RICH_CLASSES]
    rich_puts = sorted(p for p in per_put_shares if p[0].lower() in RICH_CLASSES)
    n_rich = len(rich_put_means)
    rich_mean = round(float(np.mean(rich_put_means)), 4) if n_rich else 0.0
    lower = round(boot_lower_95(rich_put_means), 4)

    # per-class (C, D) share means
    per_class = {}
    for cls in RICH_CLASSES:
        vals = [np.mean(v) for p, v in per_put_shares.items()
                if p[0].lower() == cls]
        per_class[cls.upper()] = {
            "n_puts": len(vals),
            "share_mean": round(float(np.mean(vals)), 4) if vals else None,
        }

    verdict_pass = bool(lower > GRADED_THRESHOLD)
    if verdict_pass:
        licensed = ("on rich (C/D) PUTs the declared MetaPattern carries GRADED "
                    f"attribution (rich-class mean share {rich_mean}, one-sided "
                    f"95% lower bound {lower} > {GRADED_THRESHOLD}); the declared "
                    "MetaPattern is the dominant single stratum but co-fires with "
                    "structurally-coupled neighbours — NOT a single-stratum purity "
                    "claim")
    else:
        licensed = ("graded attribution NOT confirmed: rich-class mean share "
                    f"{rich_mean} (one-sided 95% lower bound {lower} <= "
                    f"{GRADED_THRESHOLD}); achieved share + per-class breakdown "
                    f"reported factually (C={per_class['C']['share_mean']}, "
                    f"D={per_class['D']['share_mean']})")

    return {
        "hypothesis": "H4''-graded (rich-class mean primary-stratum kill share)",
        "measure": "s_m = 1[primary in flipset]/|flipset| per detected mutant; "
                   "PUT mean; rich-class (C,D) mean aggregate",
        "flip_machinery": "IMPORTED from p2.mutators.stratum_filter.audit_matrix "
                          "(constrained=ALL_FAMILIES; identical to the S5 audit)",
        "threshold": GRADED_THRESHOLD,
        "n_boot": N_BOOT, "boot_seed": MASTER_SEED, "alpha": ALPHA,
        "n_rich": n_rich,
        "rich_puts": rich_puts,
        "rich_mean_share": rich_mean,
        "boot_lower_95": lower,
        "per_class_share_mean": per_class,
        "per_put_share": per_put_mean,
        "per_put_detail": per_put_detail,
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "verdict": "CONFIRM" if verdict_pass else "NOT_CONFIRMED",
        "licensed_claim": licensed,
    }


# --------------------------------------------------------------------------- #
# H4'''-graded POOLED (Study-4 §3.2, §7b --pooled flag). ADDITIVE: this path is
# reached ONLY via --pooled; the frozen v6 default (run/analyze_graded) is
# byte-unchanged. Contract (§7b): admit the two Study-4 arm SMS pools; form the
# graded aggregate over the UNION of rich PUT-arm units (each arm's rich PUT
# contributes its own PUT-mean; a rich PUT detected in both arms contributes two
# units). All per-mutant logic (s_m, detected-only, pilot exclusion, B=10,000,
# seed 20260708) is IDENTICAL to analyze_graded; only the aggregation pools the
# arms and the verdict layer applies the recruitment gate.
# --------------------------------------------------------------------------- #
def _rich_put_means_one_arm(matrix: dict, exclude_pilots: bool = True) -> dict:
    """{PUT: mean s_m over detected rich-class mutants} for ONE arm's pool.

    Reuses the frozen flip machinery + the s_m definition of analyze_graded
    verbatim (per (put, file) uniqueness, silent-mutant drop, pilot firewall)."""
    puts_upper = _confirmatory_puts_present(matrix)
    per_mutant, _audit = flip_map(matrix, puts_upper)
    per_put_shares: dict = {}
    for (put, fname), (fc, fl, cat) in per_mutant.items():
        put_l = put.lower()
        if exclude_pilots and put_l in PILOT_PUTS:      # §2b firewall
            continue
        if fc < 1:                                      # silent -> undetected
            continue
        if put_l[0] not in RICH_CLASSES:                # rich (C, D) only
            continue
        primary = PRIMARY_CELLS_V3[put_l]
        s_m = (1.0 if primary in fl else 0.0) / fc
        per_put_shares.setdefault(put, []).append(s_m)
    return {p: float(np.mean(v)) for p, v in per_put_shares.items()}


def analyze_graded_pooled(matrix_paths: list, exclude_pilots: bool = True) -> dict:
    """Pooled two-arm rich-class graded aggregate + recruitment-gated verdict."""
    pooled_means: list = []
    pooled_units: list = []
    per_arm: dict = {}
    for path in matrix_paths:
        arm_label = _rel(path)
        matrix = load_matrix(path)
        rich_means = _rich_put_means_one_arm(matrix, exclude_pilots=exclude_pilots)
        for put, m in sorted(rich_means.items()):
            pooled_means.append(m)
            pooled_units.append({"arm": arm_label, "put": put,
                                 "put_mean_share": round(m, 4)})
        per_arm[arm_label] = {"n_rich_detected": len(rich_means),
                              "rich_puts": sorted(rich_means)}

    pooled_n_rich = len(pooled_means)                   # detected rich PUT-arm units
    rich_mean = round(float(np.mean(pooled_means)), 4) if pooled_n_rich else 0.0
    lower = round(boot_lower_95(pooled_means), 4)

    gate_ok = pooled_n_rich >= POOLED_GATE
    if not gate_ok:
        verdict = "UNDER_RECRUITED"
        licensed = ("UNDER-RECRUITED (registration §3.2 gate): detected pooled "
                    f"n_rich = {pooled_n_rich} < {POOLED_GATE}. Achieved pooled "
                    f"rich-class mean share {rich_mean} (one-sided 95% lower bound "
                    f"{lower}) reported FACTUALLY; no threshold moved, no "
                    "confirmatory verdict licensed")
    elif lower > GRADED_THRESHOLD:
        verdict = "CONFIRM"
        licensed = ("at adequate rich-class n (pooled n_rich "
                    f"{pooled_n_rich} >= {POOLED_GATE}) the declared MetaPattern "
                    f"carries GRADED attribution (pooled mean share {rich_mean}, "
                    f"one-sided 95% lower bound {lower} > {GRADED_THRESHOLD}); "
                    "dominant-but-co-firing, NOT a single-stratum purity claim")
    else:
        verdict = "MISATTRIBUTION_CONFIRMED"
        licensed = ("MISATTRIBUTION CONFIRMED as a construct property: at an "
                    f"adequate rich-class sample (pooled n_rich {pooled_n_rich} "
                    f">= {POOLED_GATE}) the attribution share is genuinely low "
                    f"(pooled mean {rich_mean}, one-sided 95% lower bound {lower} "
                    f"<= {GRADED_THRESHOLD}); the Study-3 finding is NOT a "
                    "small-sample artifact (sharp pre-declared interpretation, "
                    "§3.2 — a substantive confirmatory result about the construct)")

    per_class = {}
    for cls in RICH_CLASSES:
        vals = [u["put_mean_share"] for u in pooled_units
                if u["put"][0].lower() == cls]
        per_class[cls.upper()] = {
            "n_units": len(vals),
            "share_mean": round(float(np.mean(vals)), 4) if vals else None,
        }

    return {
        "hypothesis": "H4'''-graded POOLED (Study-4 §3.2; two-arm rich-class mean "
                      "primary-stratum kill share, recruitment-gated)",
        "measure": "s_m = 1[primary in flipset]/|flipset| per detected mutant; "
                   "PUT mean; POOLED over the union of rich (C,D) PUT-arm units",
        "flip_machinery": "IMPORTED from p2.mutators.stratum_filter.audit_matrix "
                          "(constrained=ALL_FAMILIES; identical to the S5 audit)",
        "pooling": "UNION of rich PUT-arm units across the two Study-4 arms "
                   "(a rich PUT detected in both arms contributes two units)",
        "threshold": GRADED_THRESHOLD,
        "recruitment_gate_n_rich": POOLED_GATE,
        "n_boot": N_BOOT, "boot_seed": MASTER_SEED, "alpha": ALPHA,
        "pooled_n_rich": pooled_n_rich,
        "recruitment_gate_met": bool(gate_ok),
        "pooled_rich_mean_share": rich_mean,
        "boot_lower_95": lower,
        "per_class_share_mean": per_class,
        "per_arm": per_arm,
        "pooled_units": pooled_units,
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "verdict": verdict,
        "licensed_claim": licensed,
    }


def run_pooled(matrix_paths: list, out_path=POOLED_OUT) -> dict:
    graded = analyze_graded_pooled(matrix_paths)
    report = {
        "artefact": "h4_graded_v7",
        "generated_by": "scripts/compute_h4_graded.py --pooled",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md "
                            "(§3.2 H4'''-graded pooled; §7b --pooled contract; "
                            "§4b pre-declared pooling; §2a x4 multiplier)",
        "integrity": "Pre-frozen before Study-4 data generation; ADDITIVE --pooled "
                     "path (the frozen v6 default is byte-unchanged). Any post-data "
                     "modification must be disclosed as a deviation (§5d, §8).",
        "inputs": {"arm_sms_pools": [_rel(p) for p in matrix_paths]},
        "master_seed": MASTER_SEED,
        "H4ppp_graded_pooled": graded,
    }
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_pooled_verdict(report: dict) -> None:
    g = report["H4ppp_graded_pooled"]
    print("=== Study-4 H4'''-graded POOLED verdict (Family H, §3.2) ===")
    print(f"[H4'''-graded pooled] pooled_n_rich={g['pooled_n_rich']} "
          f"(gate >= {POOLED_GATE}, met={g['recruitment_gate_met']})  "
          f"pooled_mean_share={g['pooled_rich_mean_share']:.4f}  "
          f"boot_lower_95={g['boot_lower_95']:.4f} (bar > {GRADED_THRESHOLD})")
    print(f"    per-class: C={g['per_class_share_mean']['C']['share_mean']} "
          f"D={g['per_class_share_mean']['D']['share_mean']}")
    print(f"    VERDICT: {g['verdict']} — {g['licensed_claim']}")


# --------------------------------------------------------------------------- #
# H4''-strict (§3.2)
# --------------------------------------------------------------------------- #
def analyze_strict(matrix: dict, per_mutant: dict, audit: dict,
                   exclude_pilots: bool = True) -> dict:
    """Single-stratum purity on clean {CE, HP, CF-with-screen} + screen-smoke gate."""
    clean_detected = []          # 1 if single-stratum (flip==1), else 0
    per_family = {f: {"n_detected": 0, "n_single_stratum": 0, "n_multistratum": 0}
                  for f in CLEAN_FAMILIES}
    cf_multistratum = 0
    for (put, fname), (fc, fl, cat) in per_mutant.items():
        if exclude_pilots and put.lower() in PILOT_PUTS:  # §2b firewall
            continue
        if cat not in CLEAN_FAMILIES:
            continue
        if fc < 1:                                 # undetected
            continue
        per_family[cat]["n_detected"] += 1
        if fc == 1:
            per_family[cat]["n_single_stratum"] += 1
            clean_detected.append(1)
        else:
            per_family[cat]["n_multistratum"] += 1
            clean_detected.append(0)
            if cat == "CF":
                cf_multistratum += 1

    n_clean = len(clean_detected)
    n_single = sum(clean_detected)
    purity = round(n_single / n_clean, 4) if n_clean else 0.0
    cp_lower = round(lower_cp(n_single, n_clean), 4)

    # Screen-smoke gate (§5c): the wired all-family screen MUST have matched > 0
    # candidates at admission. n_screened_candidates counts in-scope mutants
    # under the all-family audit; zero == incident-P8 silent no-op == loud FAIL.
    n_screened = int(audit["n_screened_candidates"])
    n_flagged = int(audit["n_multistratum"])
    screen_ok = n_screened > 0

    purity_ok = bool(cp_lower >= STRICT_THRESHOLD)
    verdict_pass = bool(purity_ok and screen_ok)

    if not screen_ok:
        verdict = "FAIL_SCREEN_NOOP"
        licensed = ("LOUD FAIL — the wired all-family screen matched ZERO "
                    "candidates: incident-P8 silent no-op regression "
                    "(registration §5c screen-smoke gate). The confirmatory run "
                    "is halted; this is never silently ignored")
    elif verdict_pass:
        verdict = "CONFIRM"
        licensed = ("single-stratum purity holds where coupling is absent or "
                    f"screenable (CE/HP/CF-with-screen, purity {purity}, one-"
                    f"sided 95% lower CP bound {cp_lower} >= {STRICT_THRESHOLD}); "
                    "the single-stratum σ model is valid for {CE,HP,CF-with-"
                    "screen}, NOT claimed for OS/SI/TF on rich PUTs")
    else:
        verdict = "NOT_CONFIRMED"
        escaping = sorted(f for f, r in per_family.items()
                          if r["n_multistratum"] > 0)
        licensed = ("single-stratum purity NOT confirmed: observed purity "
                    f"{purity} (one-sided 95% lower CP bound {cp_lower} < "
                    f"{STRICT_THRESHOLD}); escaping clean families reported "
                    f"factually: {escaping or 'none'}")

    return {
        "hypothesis": "H4''-strict (single-stratum purity on clean families)",
        "measure": "fraction of DETECTED clean-family {CE,HP,CF-with-screen} "
                   "mutants that are single-stratum (flip == 1)",
        "clean_families": list(CLEAN_FAMILIES),
        "threshold": STRICT_THRESHOLD,
        "alpha": ALPHA,
        "n_clean_detected": n_clean,
        "n_single_stratum": n_single,
        "purity": purity,
        "cp_lower_95": cp_lower,
        "cf_screened_out": cf_multistratum,
        "per_family": per_family,
        "n_screened_candidates": n_screened,
        "n_multistratum_flagged": n_flagged,
        "screen_matched_gt_zero": screen_ok,
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "verdict": verdict,
        "licensed_claim": licensed,
    }


# --------------------------------------------------------------------------- #
# Holm(2) family-G record (transparency; frozen per-test rules stand)
# --------------------------------------------------------------------------- #
def _family_g_holm(graded: dict, strict: dict) -> dict:
    return {
        "family": "G — Attribution (H4''-graded, H4''-strict)",
        "correction": "Holm(2) within family G; both tests one-sided at alpha=0.05",
        "note": "The frozen per-hypothesis decision rules (graded: boot_lower_95 "
                "> 0.15; strict: cp_lower_95 >= 0.90 AND screen matched > 0) are "
                "the registered verdicts (§7b). Holm(2) is recorded as the family "
                "control; no study-wide cross-family correction (Study-2 families "
                "are closed).",
        "graded_verdict": graded["verdict"],
        "strict_verdict": strict["verdict"],
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(matrix_path=MATRIX, out_path=OUT, pilot_smoke=False) -> dict:
    matrix = load_matrix(matrix_path)
    puts_upper = _puts_present(matrix, pilot_smoke=pilot_smoke)
    per_mutant, audit = flip_map(matrix, puts_upper)
    exclude_pilots = not pilot_smoke
    graded = analyze_graded(matrix, per_mutant, exclude_pilots=exclude_pilots)
    strict = analyze_strict(matrix, per_mutant, audit, exclude_pilots=exclude_pilots)
    report = {
        "artefact": "h4_graded_v6" + ("_PILOT_SMOKE" if pilot_smoke else ""),
        "generated_by": "scripts/compute_h4_graded.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY3_v2.md "
                            "(§3.1 H4''-graded; §3.2 H4''-strict; §7b contract; "
                            "§2b/§2c pilot exclusion)",
        "integrity": "Pre-frozen before Study-3 data generation; any post-data "
                     "modification must be disclosed as a deviation (§5c, §8).",
        "run_mode": "PILOT-SMOKE (NOT confirmatory; pilot pool, firewalled §2b)"
                    if pilot_smoke else "confirmatory",
        "inputs": {"per_cell_sms_matrix": _rel(matrix_path)},
        "master_seed": MASTER_SEED,
        "n_confirmatory_puts_present": len(puts_upper),
        "H4pp_graded": graded,
        "H4pp_strict": strict,
        "family_g": _family_g_holm(graded, strict),
    }
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    g, s = report["H4pp_graded"], report["H4pp_strict"]
    tag = " [PILOT-SMOKE — NOT confirmatory]" if report["run_mode"].startswith(
        "PILOT") else ""
    print(f"=== Study-3 attribution verdicts (Family G, Holm 2){tag} ===")
    print(f"[H4''-graded] n_rich={g['n_rich']}  rich_mean_share="
          f"{g['rich_mean_share']:.4f}  boot_lower_95={g['boot_lower_95']:.4f} "
          f"(bar > {GRADED_THRESHOLD})")
    print(f"    per-class: C={g['per_class_share_mean']['C']['share_mean']} "
          f"D={g['per_class_share_mean']['D']['share_mean']}")
    print(f"    VERDICT: {g['verdict']} — {g['licensed_claim']}")
    print(f"[H4''-strict] purity={s['purity']:.4f}  cp_lower_95="
          f"{s['cp_lower_95']:.4f} (bar >= {STRICT_THRESHOLD})  "
          f"screen_matched={s['n_screened_candidates']} "
          f"flagged={s['n_multistratum_flagged']}")
    print(f"    VERDICT: {s['verdict']} — {s['licensed_claim']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrix", default=str(MATRIX),
                    help="per-cell SMS matrix SSOT (fresh Study-3 v6 pool)")
    ap.add_argument("--out", default=str(OUT),
                    help="output SSOT path ('-' = stdout only, no file write)")
    ap.add_argument("--pilot-smoke", dest="pilot_smoke", action="store_true",
                    help="clearly-labelled PILOT smoke run: consume a pilot SMS "
                         "matrix end-to-end (NOT a confirmatory verdict; §2b "
                         "firewall). Marks the artefact and refuses to overwrite "
                         "the confirmatory SSOT.")
    ap.add_argument("--pooled", nargs="+", default=None, metavar="ARM_SMS",
                    help="Study-4 §7b: pool >=2 arm SMS pool SSOTs and compute the "
                         "recruitment-gated H4'''-graded verdict (pooled n_rich "
                         ">= 24 gate, then boot_lower_95 > 0.15). Writes "
                         "data/results/h4_graded_v7.json by default. ADDITIVE: "
                         "does not touch the frozen v6 default path.")
    args = ap.parse_args()

    if args.pooled is not None:
        if len(args.pooled) < 2:
            print("ERROR: --pooled requires >= 2 arm SMS pool SSOTs "
                  "(same-source + cross-source).", file=sys.stderr)
            return 2
        missing = [p for p in args.pooled if not Path(p).exists()]
        if missing:
            print("ERROR: pooled arm SMS pool SSOT(s) missing: "
                  f"{missing}\nThis runs on the ANALYSIS leg, AFTER Study-4 SMS "
                  "scoring of the fresh v7 arm pools. No Study-4 confirmatory data "
                  "exists yet at freeze time (registration §0.1).", file=sys.stderr)
            return 2
        out_path = None if args.out == "-" else (
            str(POOLED_OUT) if args.out == str(OUT) else args.out)
        report = run_pooled(args.pooled, out_path)
        _print_pooled_verdict(report)
        if out_path is not None:
            print(f"\nwrote {out_path}")
        return 0
    if not Path(args.matrix).exists():
        print(f"ERROR: per-cell SMS matrix SSOT missing: {args.matrix}\n"
              "This script runs on the ANALYSIS leg, AFTER Study-3 SMS scoring "
              "of the fresh v6 pool. No Study-3 confirmatory data exists yet at "
              "freeze time (registration §0.1).", file=sys.stderr)
        return 2
    out_path = None if args.out == "-" else args.out
    if args.pilot_smoke and out_path is not None and Path(out_path).resolve() == OUT.resolve():
        print("ERROR: refusing to write the confirmatory SSOT "
              f"({_rel(OUT)}) from a --pilot-smoke run. Use a *_pilot output "
              "path or '-' (§2b firewall).", file=sys.stderr)
        return 2
    report = run(args.matrix, out_path, pilot_smoke=args.pilot_smoke)
    _print_verdicts(report)
    if out_path is not None:
        print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
