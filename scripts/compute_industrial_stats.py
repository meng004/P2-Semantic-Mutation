#!/usr/bin/env python3
"""Study-2 confirmatory analysis — two-tier industrial census (H2-3, H2-4).

Pre-frozen under PREREGISTRATION_STUDY2.md before Study-2 data generation; any
post-data modification must be disclosed as a deviation.

Implements EXACTLY the registered two-tier industrial plan
(PREREGISTRATION_STUDY2.md §3 H2-3/H2-4, §6):

  Tier A (verified_full) is the ONLY tier that enters the primary confirmatory
  estimand. Tier B (reproduced-but-unfixed, local-patch fixed arm) is reported
  in a SEPARATE sensitivity stratum and is NEVER pooled into the primary
  estimand or relabeled verified_full (§6.1).

  Family C — H2-3 (RQ-S2c), Holm across 3 one-sided Wilcoxon signed-rank
    contrasts on case-level paired kill-rate differences over Tier A:
      H2-3a T1>B1, H2-3b T1>A1, H2-3c B1>B2.
    Decision (§3 H2-3):
      * Tier A >= 45              -> Holm-adjusted p < 0.05 => CONFIRM that contrast.
      * Tier A  < 45 (expected)   -> H2-3a reported UNDER-RECRUITED with its
                                     achieved-n Wilcoxon power; confirmatory
                                     weight shifts to the sign-flip robustness
                                     + H2-4 incidence (both adequately powered).
    Robustness of the SAME T1>B1 estimand (not a new hypothesis, §3): exact
    sign-flip permutation on the Wilcoxon rank statistic, Monte-Carlo sign-flip
    on the mean paired difference, and a BCa CI for Cliff's delta.

  Family D — H2-4 (RQ-S2c), SEPARATE from Holm family C (§3 H2-4): 2x2 Fisher
    exact, one-sided, T1 detection incidence > B1 detection incidence over
    Tier A. Decision: p < 0.05 => CONFIRM incidence separation. This leg stays
    confirmatory even under Tier-A under-recruitment (power 1.00 at every n).

  E-PETSC-004 (§6.4): already verified_full but results-partial at Study-1;
  Study 2 registers completion of its mutation run, extending Tier A 34 -> 35.
  Its completion status is reported; a case with no applied mutants is excluded
  from the analysis until its run completes.

INTEGRITY. Pure function of the frozen per-case census SSOT + the power SSOT +
the registered constants below. No tunable knob outside the registration; no
data peeking. The statistics kit (Wilcoxon signed-rank with exact sign-flip DP,
Holm, Cliff's delta, percentile/BCa bootstrap, MC sign-flip) is method-identical
to scripts/build_industrial_ssot.py (the Study-1 SSOT builder) so Family C is
"exactly as Study 1" (§3).

Inputs (registration §7 SSOT paths):
  frozen per-case census : data/results/industrial_percase_v2.json
  power reference        : data/results/power_study2.json
Output:
  data/results/industrial_stats_v2.json

Usage:
    PYTHONPATH=src python3 scripts/compute_industrial_stats.py
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import random
import sys
from pathlib import Path
from statistics import NormalDist

from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY2.md §3, §6, §7) ----------
GROUPS = ["T1", "B1", "B2", "A1"]
PAIRS = [("T1", "B1"), ("T1", "A1"), ("B1", "B2")]   # Family C, Holm over 3
TIER_A_CONFIRMATORY_FLOOR = 45      # §3/§6.5: Tier A >= 45 => H2-3 confirmatory
ALPHA = 0.05
BOOT_B = 10_000
BOOT_SEED = 20260708                # §7 Study-2 master seed (Study-1 used 20260704)
EPETSC004 = "E-PETSC-004"
Z95 = 1.959963984540054

PERCASE = RESULTS / "industrial_percase_v2.json"
POWER = RESULTS / "power_study2.json"
OUT = RESULTS / "industrial_stats_v2.json"


# --------------------------------------------------------------------------- #
# Statistics kit (method-identical to scripts/build_industrial_ssot.py)
# --------------------------------------------------------------------------- #
def _avg_ranks(absd):
    n = len(absd)
    ranks, i = [0.0] * n, 0
    while i < n:
        j = i
        while j + 1 < n and absd[j + 1] == absd[i]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    return ranks


def wilcoxon_stats(diffs):
    """One-sided (H1: median > 0) signed-rank. Returns W+ (=V), n_eff, z
    (tie-corrected, 0.5 continuity), normal-approx p, and the EXACT sign-flip
    permutation p on the rank statistic (DP over 2x-scaled ranks). Degenerate
    all-zero input -> null (p=1.0)."""
    d = [x for x in diffs if x != 0.0]
    n = len(d)
    if n == 0:
        return {"V_wplus": 0.0, "n_eff": 0, "z": 0.0,
                "p_normal_one_sided": 1.0, "p_exact_sign_flip_rank": 1.0}
    pairs = sorted((abs(x), x > 0) for x in d)
    ranks = _avg_ranks([a for a, _ in pairs])
    wplus = sum(r for r, (_, pos) in zip(ranks, pairs) if pos)
    mu = n * (n + 1) / 4
    cnt = collections.Counter(a for a, _ in pairs)
    tiesum = sum(t ** 3 - t for t in cnt.values())
    var = n * (n + 1) * (2 * n + 1) / 24 - tiesum / 48
    z = (wplus - mu - 0.5) / math.sqrt(var) if var > 0 else 0.0
    p_norm = 0.5 * math.erfc(z / math.sqrt(2))
    sr = [int(round(2 * r)) for r in ranks]
    tot = sum(sr)
    dp = [0] * (tot + 1)
    dp[0] = 1
    for r in sr:
        for s in range(tot, r - 1, -1):
            dp[s] += dp[s - r]
    target = int(round(2 * wplus))
    p_exact = sum(dp[target:]) / (2 ** n)
    return {"V_wplus": wplus, "n_eff": n, "z": round(z, 4),
            "p_normal_one_sided": p_norm, "p_exact_sign_flip_rank": p_exact}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, mx = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        mx = max(mx, min(1.0, (len(ps) - rank) * ps[i]))
        out[i] = mx
    return out


def cliffs_delta(a, b):
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    return (gt - lt) / (len(a) * len(b)) if a and b else 0.0


def boot_mean_ci(diffs, B=BOOT_B, seed=BOOT_SEED):
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(B))
    return means[int(0.025 * B)], means[int(0.975 * B) - 1]


def signflip_mean_p(diffs, B=BOOT_B, seed=BOOT_SEED):
    rng = random.Random(seed)
    obs = sum(diffs) / len(diffs)
    hits = 0
    for _ in range(B):
        s = sum(x if rng.random() < 0.5 else -x for x in diffs)
        if s / len(diffs) >= obs - 1e-15:
            hits += 1
    return (hits + 1) / (B + 1)


def bca_delta_ci(a, b, B=BOOT_B, seed=BOOT_SEED, alpha=0.05):
    n = len(a)
    obs = cliffs_delta(a, b)
    rng = random.Random(seed)
    boots = []
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        boots.append(cliffs_delta([a[i] for i in idx], [b[i] for i in idx]))
    boots.sort()
    nd = NormalDist()
    prop = sum(1 for x in boots if x < obs) / B
    prop = min(max(prop, 1.0 / B), 1 - 1.0 / B)
    z0 = nd.inv_cdf(prop)
    jack = []
    for i in range(n):
        jack.append(cliffs_delta(a[:i] + a[i + 1:], b[:i] + b[i + 1:]))
    jm = sum(jack) / n
    num = sum((jm - x) ** 3 for x in jack)
    den = 6.0 * (sum((jm - x) ** 2 for x in jack) ** 1.5)
    acc = num / den if den != 0 else 0.0
    out = []
    for zq in (nd.inv_cdf(alpha / 2), nd.inv_cdf(1 - alpha / 2)):
        adj = nd.cdf(z0 + (z0 + zq) / (1 - acc * (z0 + zq)))
        k = min(max(int(adj * B), 0), B - 1)
        out.append(boots[k])
    return out[0], out[1]


# --------------------------------------------------------------------------- #
# Census ingestion + tiering (§6)
# --------------------------------------------------------------------------- #
def partition_tiers(cases: dict):
    """Return (tier_a_ids, tier_b_ids) with analysable cases only.

    A case is analysable iff it has applied mutants (n_applied > 0). Cases with
    no tier tag default to Tier A (Study-1's census is verified_full).
    """
    tier_a, tier_b, excluded = [], [], []
    for cid, rec in cases.items():
        if rec.get("n_applied", 0) <= 0:
            excluded.append(cid)
            continue
        (tier_b if rec.get("tier", "A") == "B" else tier_a).append(cid)
    return sorted(tier_a), sorted(tier_b), sorted(excluded)


def epetsc004_status(cases: dict) -> dict:
    """§6.4 completion handling for E-PETSC-004."""
    rec = cases.get(EPETSC004)
    if rec is None:
        return {"present": False,
                "status": "absent — Tier A remains at the Study-1 floor of 34"}
    n = rec.get("n_applied", 0)
    if n > 0 and rec.get("kills"):
        return {"present": True, "tier": rec.get("tier", "A"), "n_applied": n,
                "status": "complete — mutation run finished; extends Tier A 34 -> 35"}
    return {"present": True, "tier": rec.get("tier", "A"), "n_applied": n,
            "status": "results-partial — mutation run incomplete; EXCLUDED "
                      "until completion (§6.4)"}


# --------------------------------------------------------------------------- #
# Family C — H2-3 Holm-3 Wilcoxon + robustness battery
# --------------------------------------------------------------------------- #
def paired_family(cases: dict, ids: list, B=BOOT_B, seed=BOOT_SEED):
    kr = {c: {g: cases[c]["kills"][g] / cases[c]["n_applied"] for g in GROUPS}
          for c in ids}
    rows = []
    for g1, g2 in PAIRS:
        diffs = [kr[c][g1] - kr[c][g2] for c in ids]
        w = wilcoxon_stats(diffs)
        lo, hi = boot_mean_ci(diffs, B=B, seed=seed)
        delta = cliffs_delta([kr[c][g1] for c in ids], [kr[c][g2] for c in ids])
        rows.append({
            "comparison": f"{g1}>{g2}",
            "mean_paired_diff": round(sum(diffs) / len(diffs), 4),
            "bootstrap_percentile_ci95": [round(lo, 4), round(hi, 4)],
            "wilcoxon": w,
            "cliffs_delta": round(delta, 4),
            "_diffs": diffs,
            "_a": [kr[c][g1] for c in ids],
            "_b": [kr[c][g2] for c in ids],
        })
    adj = holm([r["wilcoxon"]["p_normal_one_sided"] for r in rows])
    for r, pa in zip(rows, adj):
        r["holm_adjusted_p"] = round(pa, 4)
        r["wilcoxon"]["p_normal_one_sided"] = round(r["wilcoxon"]["p_normal_one_sided"], 4)
        r["wilcoxon"]["p_exact_sign_flip_rank"] = round(r["wilcoxon"]["p_exact_sign_flip_rank"], 5)
    return rows


def achieved_n_power(power_json: dict, n: int) -> dict:
    wp = power_json["c_industrial_expansion"]["wilcoxon_power"]
    sf = power_json["c_industrial_expansion"]["signflip_power"]
    keys = sorted(int(k) for k in wp)
    nearest = min(keys, key=lambda k: (abs(k - n), k))
    return {"achieved_n": n, "nearest_registered_grid_n": nearest,
            "wilcoxon_power_at_grid": wp[str(nearest)],
            "signflip_power_at_grid": sf[str(nearest)]}


def h2_3(cases: dict, tier_a: list, power_json: dict, B=BOOT_B, seed=BOOT_SEED) -> dict:
    n_a = len(tier_a)
    family = paired_family(cases, tier_a, B=B, seed=seed)
    t1b1 = family[0]

    # robustness battery on the SAME T1>B1 estimand (§3)
    diffs = t1b1["_diffs"]
    battery = {
        "estimand": "one-sided case-level T1>B1 paired contrast (identical to "
                    "the Holm-family member; robustness, not a new hypothesis)",
        "exact_sign_flip_permutation_on_rank_statistic": {
            "n_eff_nonzero_diffs": t1b1["wilcoxon"]["n_eff"],
            "p_one_sided": t1b1["wilcoxon"]["p_exact_sign_flip_rank"],
        },
        "monte_carlo_sign_flip_on_mean_diff": {
            "B": B, "seed": seed,
            "p_one_sided": round(signflip_mean_p(diffs, B=B, seed=seed), 5),
        },
        "bca_bootstrap_ci_cliffs_delta": None,
    }
    bca_lo, bca_hi = bca_delta_ci(t1b1["_a"], t1b1["_b"], B=B, seed=seed)
    battery["bca_bootstrap_ci_cliffs_delta"] = {
        "B": B, "seed": seed, "ci95": [round(bca_lo, 4), round(bca_hi, 4)],
        "excludes_zero": bca_lo > 0,
    }

    confirmatory = n_a >= TIER_A_CONFIRMATORY_FLOOR
    verdicts = {}
    for r in family:
        comp = r["comparison"]
        if confirmatory:
            verdicts[comp] = ("CONFIRM" if r["holm_adjusted_p"] < ALPHA
                              else "NOT_CONFIRMED")
        elif comp == "T1>B1":
            verdicts[comp] = "UNDER_RECRUITED"
        else:
            verdicts[comp] = "REPORTED_DESCRIPTIVE (Tier A < 45)"

    for r in family:
        for k in ("_diffs", "_a", "_b"):
            r.pop(k, None)

    out = {
        "family": "C — Industrial mutation-phase (Holm over 3, confirmatory)",
        "scope": "Tier A (verified_full) only; Tier B never enters this estimand",
        "tier_a_n": n_a,
        "confirmatory_floor": TIER_A_CONFIRMATORY_FLOOR,
        "confirmatory_regime": confirmatory,
        "holm_family": family,
        "verdicts": verdicts,
        "robustness_battery_T1_gt_B1": battery,
    }
    if not confirmatory:
        out["under_recruitment"] = {
            "note": "Tier A < 45 (expected per §6 E3 triage): H2-3a magnitude is "
                    "UNDER-RECRUITED; no threshold moving, no Tier-B pooling. "
                    "Confirmatory weight shifts to the sign-flip robustness "
                    "and the H2-4 incidence leg.",
            "achieved_n_power": achieved_n_power(power_json, n_a),
        }
    return out


# --------------------------------------------------------------------------- #
# Family D — H2-4 Fisher incidence (SEPARATE from Holm family C)
# --------------------------------------------------------------------------- #
def _detect_counts(cases: dict, ids: list):
    t1 = sum(1 for c in ids if cases[c]["face"]["t1"] == "DETECT")
    b1 = sum(1 for c in ids if cases[c]["face"]["b1"])   # b1>0 => B1 detected
    return t1, b1


def h2_4(cases: dict, tier_a: list) -> dict:
    n = len(tier_a)
    t1, b1 = _detect_counts(cases, tier_a)
    table = [[t1, n - t1], [b1, n - b1]]
    _, p = fisher_exact(table, alternative="greater")
    verdict = "CONFIRM" if p < ALPHA else "NOT_CONFIRMED"
    return {
        "family": "D — Industrial incidence (single test, OUTSIDE Holm family C)",
        "scope": "Tier A only (face-level, per case)",
        "statistic": "2x2 Fisher exact, one-sided (T1 incidence > B1 incidence)",
        "t1_detect": t1, "b1_detect": b1, "n_cases": n,
        "contingency_table": table,
        "fisher_p_one_sided": float(p),
        "verdict": verdict,
        "licensed_claim": (
            "incidence separation is a DISTINCT estimand from magnitude "
            "dominance (H2-3); reported side by side, never merged. Case "
            "admission conditions on MR-detectability, so the face reads as "
            "construct separation among admitted cases, not a coverage rate."),
    }


# --------------------------------------------------------------------------- #
# Tier B sensitivity stratum (SEPARATE; never pooled — §6.5)
# --------------------------------------------------------------------------- #
def tier_b_sensitivity(cases: dict, tier_b: list, B=BOOT_B, seed=BOOT_SEED) -> dict:
    if not tier_b:
        return {"n_cases": 0,
                "note": "no Tier B (reproduced-but-unfixed) cases in the frozen census"}
    family = paired_family(cases, tier_b, B=B, seed=seed)
    t1, b1 = _detect_counts(cases, tier_b)
    for r in family:
        for k in ("_diffs", "_a", "_b"):
            r.pop(k, None)
    return {
        "label": "SENSITIVITY STRATUM (open-unfixed, local-patch fixed arm) — "
                 "NEVER pooled into the primary estimand, NEVER relabeled "
                 "verified_full (§6.1, §6.5)",
        "n_cases": len(tier_b),
        "case_ids": tier_b,
        "paired_family": family,
        "face_incidence": {"t1_detect": t1, "b1_detect": b1, "n": len(tier_b)},
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(percase_path=PERCASE, power_path=POWER, out_path=OUT,
        B=BOOT_B, seed=BOOT_SEED) -> dict:
    pc = json.loads(Path(percase_path).read_text())
    cases = pc["cases"]
    power_json = json.loads(Path(power_path).read_text())

    tier_a, tier_b, excluded = partition_tiers(cases)
    report = {
        "artefact": "industrial_stats_v2",
        "generated_by": "scripts/compute_industrial_stats.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY2.md "
                            "(§3 H2-3/H2-4; §6 two-tier census; §7 SSOT/seeds)",
        "integrity": "Pre-frozen before Study-2 data generation; any post-data "
                     "modification must be disclosed as a deviation.",
        "derives_from": str(Path(percase_path).name),
        "master_seed": seed,
        "bootstrap_B": B,
        "census": {
            "tier_a_n": len(tier_a), "tier_a_ids": tier_a,
            "tier_b_n": len(tier_b), "tier_b_ids": tier_b,
            "excluded_no_applied_mutants": excluded,
        },
        "epetsc004_completion": epetsc004_status(cases),
        "H2_3_mutation_phase_dominance": h2_3(cases, tier_a, power_json, B=B, seed=seed),
        "H2_4_detection_incidence": h2_4(cases, tier_a),
        "tier_b_sensitivity_stratum": tier_b_sensitivity(cases, tier_b, B=B, seed=seed),
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    h3 = report["H2_3_mutation_phase_dominance"]
    h4 = report["H2_4_detection_incidence"]
    print("=== Study-2 industrial confirmatory verdicts (two-tier census) ===")
    print(f"Tier A n = {report['census']['tier_a_n']} "
          f"(confirmatory floor {h3['confirmatory_floor']}; "
          f"regime={'CONFIRMATORY' if h3['confirmatory_regime'] else 'UNDER-RECRUITED'})")
    print(f"E-PETSC-004: {report['epetsc004_completion']['status']}")
    print("[H2-3 / Family C — Holm-3 Wilcoxon]")
    for r in h3["holm_family"]:
        comp = r["comparison"]
        print(f"    {comp:8s} mean_diff={r['mean_paired_diff']:+.4f} "
              f"Holm p={r['holm_adjusted_p']:.4f} "
              f"delta={r['cliffs_delta']:+.4f} -> {h3['verdicts'][comp]}")
    b = h3["robustness_battery_T1_gt_B1"]
    print(f"    robustness T1>B1: exact sign-flip p="
          f"{b['exact_sign_flip_permutation_on_rank_statistic']['p_one_sided']}, "
          f"MC sign-flip p={b['monte_carlo_sign_flip_on_mean_diff']['p_one_sided']}, "
          f"BCa delta CI={b['bca_bootstrap_ci_cliffs_delta']['ci95']}")
    if "under_recruitment" in h3:
        ap = h3["under_recruitment"]["achieved_n_power"]
        print(f"    under-recruited: achieved-n Wilcoxon power ~ "
              f"{ap['wilcoxon_power_at_grid']} (grid n={ap['nearest_registered_grid_n']})")
    print(f"[H2-4 / Family D — Fisher incidence] "
          f"T1 {h4['t1_detect']}/{h4['n_cases']} vs B1 {h4['b1_detect']}/{h4['n_cases']} "
          f"p={h4['fisher_p_one_sided']:.3g} -> {h4['verdict']}")
    tb = report["tier_b_sensitivity_stratum"]
    print(f"[Tier B sensitivity] n={tb['n_cases']} (separate; never pooled)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--percase", default=str(PERCASE),
                    help="frozen per-case census SSOT (v2)")
    ap.add_argument("--power", default=str(POWER), help="power reference SSOT")
    ap.add_argument("--out", default=str(OUT), help="output SSOT path")
    args = ap.parse_args()
    if not Path(args.percase).exists():
        print(f"ERROR: census SSOT missing: {args.percase}\n"
              "This script runs on the ANALYSIS leg, after the Study-2 census "
              "is frozen (§6.5). No Study-2 census exists yet at freeze time.",
              file=sys.stderr)
        return 2
    report = run(args.percase, args.power, args.out)
    _print_verdicts(report)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
