#!/usr/bin/env python3
"""Build and verify the in-repo SSOT for the industrial (RQ4) arm.

Closes R1 Major M1 / R3 Major M1 (industrial-arm reproducibility): every
paper-cited industrial number is derived from the per-case matrix in
`data/results/industrial_percase_v1.json`, which is extracted from the
Defect4MR deposit (Zenodo DOI 10.5281/zenodo.21203424, record 21203937,
P12-Defect4MR-1.0.1.zip).

Modes
-----
  python3 scripts/build_industrial_ssot.py
      Derive mode (default): read data/results/industrial_percase_v1.json,
      re-derive every paper-cited industrial number, run the R3 strengthening
      battery, write data/results/industrial_arm_v1.json and
      data/results/industrial_stats_v1.json. Exits nonzero on any mismatch.

  python3 scripts/build_industrial_ssot.py --extract <deposit_root>
      Extract mode: parse <deposit_root>/data/mutation/results.jsonl (per-case
      x per-MR mutant verdicts) and REALDEFECT-FACE.md (30-row real-defect
      face) from a local copy of the Defect4MR deposit and write
      data/results/industrial_percase_v1.json. The four 2026-07-05 extension
      cases (absent from the 30-row face table) carry face rows transcribed
      from their per-case NOTES.md real-defect-face tables (source paths
      recorded per row).

Statistical plan (mirrors the dataset's pre-registered plan, design §6 of the
deposit's docs/mutation_phase_design.md; independently re-implemented here):
  kill = verdict 'kill' (oracle VIOLATED | crash | timeout); 'nocompile'
  excluded from the denominator; group kill = any MR of the group kills the
  mutant; primary denominator = all applied mutants. Paired family
  T1>B1, T1>A1, B1>B2: one-sided Wilcoxon signed-rank (zeros discarded,
  average ranks, normal approximation with tie correction and 0.5 continuity
  for n_eff>25), Holm correction; case-resampling percentile bootstrap
  (B=10000, seed 20260704) for the mean paired difference; Cliff's delta on
  the two case-level KR vectors.

Strengthening battery (R3 M1; SAME estimand, the one-sided T1>B1 case-level
paired contrast -- no HARKing):
  1. Exact sign-flip permutation test on the Wilcoxon signed-rank statistic
     (full 2^n_eff null via dynamic programming over tie-averaged ranks
     scaled x2 to integers; exact, not sampled).
  2. Monte Carlo sign-flip permutation test on the MEAN paired difference
     (B=10000, seed 20260704; exact enumeration of 2^n_eff means is
     infeasible for real-valued means).
  3. BCa bootstrap CI for Cliff's delta (paired case-resampling, B=10000,
     seed 20260704, jackknife acceleration).
  4. Wilcoxon V (= W+) and z, with the unadjusted one-sided p.

No number in the output is hand-typed: everything derives from the per-case
matrix. Pure Python (no numpy/scipy).
"""
import argparse
import collections
import json
import math
import os
import random
import re
import sys
from statistics import NormalDist

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "data", "results")
PERCASE = os.path.join(RESULTS_DIR, "industrial_percase_v1.json")

GROUPS = ["T1", "B1", "B2", "A1"]
PAIRS = [("T1", "B1"), ("T1", "A1"), ("B1", "B2")]  # pre-registered family
SENS_EXCLUDE = "E-SUNDIALS-005"
BOOT_B = 10000
BOOT_SEED = 20260704
Z95 = 1.959963984540054

PROVENANCE = {
    "dataset": "Defect4MR (P12), version 1.0.1",
    "doi": "10.5281/zenodo.21203424",
    "zenodo_record": "21203937",
    "deposit_file": "P12-Defect4MR-1.0.1.zip",
    "deposit_zip_sha256":
        "39c53ef016accf7d0108827a41f4284e0437aad7300eb01970adf4ce3433eb7f",
    "source_files_within_deposit": [
        "data/mutation/results.jsonl (10250 rows, 34 cases, per-mutant "
        "per-MR verdicts)",
        "data/mutation/REALDEFECT-FACE.md (30-row real-defect face master "
        "table)",
        "data/mutation/{a-lapack-004,a-openblas-001,b-pocketfft-002,"
        "e-ordinarydiffeq-001}/NOTES.md (real-defect face tables of the four "
        "2026-07-05 extension cases)",
        "reports/cloud/mutation-final-stats-2026-07-04.md (pre-registered "
        "statistics report; Appendix B = 34-case rerun)",
    ],
    "prereg_plan": "deposit docs/mutation_phase_design.md section 6; "
                   "reference implementation tools/mutstats/prereg_stats.py "
                   "(re-implemented independently in this script)",
}

# Real-defect face rows of the four extension cases, transcribed from the
# per-case NOTES.md "Real-defect face" tables (the 30-row master table
# REALDEFECT-FACE.md predates the 2026-07-05 extension). b1/b2 = number of
# the 3 group relations violated on the buggy arm; a1a/a1b = ablation
# RETAIN/LOSE of the real defect.
EXTENSION_FACE = {
    "A-LAPACK-004": {
        "t1": "DETECT", "b1": 0, "b2": 0, "a1a": "LOSE", "a1b": "LOSE",
        "source": "data/mutation/a-lapack-004/NOTES.md (T1 VIOLATED 1/1; "
                  "B1 0/3; B2 0/3; A1 0/2 -- both ablations miss)",
    },
    "A-OPENBLAS-001": {
        "t1": "DETECT", "b1": 1, "b2": 1, "a1a": "RETAIN", "a1b": "RETAIN",
        "source": "data/mutation/a-openblas-001/NOTES.md (T1 VIOLATED; "
                  "B1-3 VIOLATED; B2-3 VIOLATED; A1-a/A1-b VIOLATED = retain)",
    },
    "B-POCKETFFT-002": {
        "t1": "DETECT", "b1": 2, "b2": 1, "a1a": "RETAIN", "a1b": "RETAIN",
        "source": "data/mutation/b-pocketfft-002/NOTES.md (T1 KILL; B1-2/B1-3 "
                  "KILL(HANG); B2-6 KILL(HANG); A1-a/A1-b KILL = retain)",
    },
    "E-ORDINARYDIFFEQ-001": {
        "t1": "DETECT", "b1": 1, "b2": 0, "a1a": "LOSE", "a1b": "RETAIN",
        "source": "data/mutation/e-ordinarydiffeq-001/NOTES.md ('T1 DETECTS | "
                  "B1 1/3 (B1-3 only) | B2 0/3 | A1-a LOSES, A1-b DETECTS')",
    },
}

# Paper-cited values (source/main.tex L2434-2487; source/supplementary.tex
# Appendix I tab:realdefect-ledger). Used ONLY as expectations to verify
# derived values against; never copied into derived output.
PAPER = {
    "n_cases": 34, "denominator": 1124,
    "kills": {"T1": 377, "A1": 348, "B1": 274, "B2": 228},
    "t1_wilson": [0.308, 0.364],
    "rates": {"T1": 0.335, "A1": 0.310, "B1": 0.244, "B2": 0.203},
    "mean_paired_diff": 0.101, "boot_ci": [0.029, 0.179],
    "holm_p": 0.046, "cliffs_delta": 0.247,
    "face_t1": 34, "face_b1_miss": 27, "face_b2_miss": 26,
    "face_a1a_lose": 19, "face_a1b_lose": 17, "face_shared_lose": 11,
}


# ------------------------------- extract mode -------------------------------

def extract(deposit_root):
    jsonl = os.path.join(deposit_root, "data", "mutation", "results.jsonl")
    facemd = os.path.join(deposit_root, "data", "mutation",
                          "REALDEFECT-FACE.md")
    by = collections.defaultdict(lambda: collections.defaultdict(dict))
    n_rows = 0
    for line in open(jsonl):
        r = json.loads(line)
        n_rows += 1
        if r.get("mr_id"):
            by[r["case"]][r["mutant_id"]][r["mr_id"]] = r

    def group_of(mr):
        return "T1" if mr == "T1" else mr[:2]

    cases = {}
    for case in sorted(by):
        applied, kills = set(), {g: set() for g in GROUPS}
        for mid, mrs in by[case].items():
            rows = [r for r in mrs.values() if r["verdict"] != "nocompile"]
            if not rows:
                continue
            applied.add(mid)
            for r in rows:
                if r["verdict"] == "kill":
                    kills[group_of(r["mr_id"])].add(mid)
        cases[case] = {
            "n_applied": len(applied),
            "kills": {g: len(kills[g] & applied) for g in GROUPS},
        }

    # 30-row face master table
    face = {}
    row_re = re.compile(
        r"^\|\s*([a-z0-9-]+)\s*\|\s*(DETECT|MISS)\s*\|\s*(\d)/3\s*\|"
        r"\s*(\d)/3\s*\|\s*(RETAIN|LOSE)\s*\|\s*(RETAIN|LOSE)\s*\|")
    for line in open(facemd):
        m = row_re.match(line)
        if m:
            face[m.group(1).upper()] = {
                "t1": m.group(2), "b1": int(m.group(3)), "b2": int(m.group(4)),
                "a1a": m.group(5), "a1b": m.group(6),
                "source": "data/mutation/REALDEFECT-FACE.md",
            }
    face.update(EXTENSION_FACE)

    missing = sorted(set(cases) - set(face))
    if missing:
        raise SystemExit("face rows missing for: %s" % missing)

    for case in cases:
        cases[case]["face"] = face[case]

    out = {
        "artefact": "industrial_percase_v1",
        "description": "Per-case industrial (RQ4) matrix: mutation-phase "
                       "kill counts per arm (all-applied denominator) and "
                       "real-defect face per case.",
        "provenance": dict(PROVENANCE, results_jsonl_rows=n_rows),
        "groups": {"T1": "registered pattern-derived relation",
                   "B1": "literature-generic baselines (3 relations)",
                   "B2": "seeded random relations (3 relations)",
                   "A1": "mechanical ablations of T1 (A1-a dimension-"
                         "reduction, A1-b de-strictification)"},
        "kill_semantics": "kill = oracle VIOLATED | crash | timeout(10x); "
                          "nocompile excluded from denominator; group kill = "
                          "any MR of the group kills the mutant",
        "cases": cases,
    }
    with open(PERCASE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("wrote %s (%d cases, %d applied mutants)"
          % (PERCASE, len(cases), sum(c["n_applied"] for c in cases.values())))


# ----------------------------- statistics kit ------------------------------

def wilson(k, n, z=Z95):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return {"rate": round(p, 3), "ci95": [round(c - h, 3), round(c + h, 3)]}


def _avg_ranks(absd):
    """absd: sorted list of |d|. Returns average ranks (1-based)."""
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
    """One-sided (H1: median > 0) signed-rank. Returns dict with W+ (=V),
    n_eff, z (tie-corrected, 0.5 continuity), normal-approx p, and the EXACT
    sign-flip permutation p on the rank statistic (DP over 2x-scaled ranks)."""
    d = [x for x in diffs if x != 0.0]
    n = len(d)
    pairs = sorted((abs(x), x > 0) for x in d)
    ranks = _avg_ranks([a for a, _ in pairs])
    wplus = sum(r for r, (_, pos) in zip(ranks, pairs) if pos)
    mu = n * (n + 1) / 4
    cnt = collections.Counter(a for a, _ in pairs)
    tiesum = sum(t ** 3 - t for t in cnt.values())
    var = n * (n + 1) * (2 * n + 1) / 24 - tiesum / 48
    z = (wplus - mu - 0.5) / math.sqrt(var)
    p_norm = 0.5 * math.erfc(z / math.sqrt(2))
    # exact permutation null of W+ over all 2^n sign assignments:
    # scale average ranks x2 -> integers; DP counts sign-subsets by rank sum.
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
    return (gt - lt) / (len(a) * len(b))


def boot_mean_ci(diffs, B=BOOT_B, seed=BOOT_SEED):
    """Case-resampling percentile CI for the mean paired difference,
    procedure-identical to the pre-registered plan (B=10000, seed 20260704,
    percentile indices floor(0.025B) and floor(0.975B)-1)."""
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(sum(rng.choice(diffs) for _ in range(n)) / n
                   for _ in range(B))
    return means[int(0.025 * B)], means[int(0.975 * B) - 1]


def signflip_mean_p(diffs, B=BOOT_B, seed=BOOT_SEED):
    """Monte Carlo sign-flip permutation p (one-sided, H1: mean > 0) on the
    mean paired difference. Zeros are sign-invariant and retained."""
    rng = random.Random(seed)
    obs = sum(diffs) / len(diffs)
    hits = 0
    for _ in range(B):
        s = sum(x if rng.random() < 0.5 else -x for x in diffs)
        if s / len(diffs) >= obs - 1e-15:
            hits += 1
    return (hits + 1) / (B + 1)  # add-one permutation-p convention


def bca_delta_ci(a, b, B=BOOT_B, seed=BOOT_SEED, alpha=0.05):
    """BCa bootstrap CI for Cliff's delta between paired case-level vectors
    a, b (paired case resampling; jackknife acceleration)."""
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
        aa = a[:i] + a[i + 1:]
        bb = b[:i] + b[i + 1:]
        jack.append(cliffs_delta(aa, bb))
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


# ------------------------------- derive mode --------------------------------

def paired_family(cases, case_ids):
    """Pre-registered 3-comparison family on the given cases."""
    kr = {c: {g: cases[c]["kills"][g] / cases[c]["n_applied"]
              for g in GROUPS} for c in case_ids}
    rows = []
    for g1, g2 in PAIRS:
        diffs = [kr[c][g1] - kr[c][g2] for c in case_ids]
        w = wilcoxon_stats(diffs)
        lo, hi = boot_mean_ci(diffs)
        delta = cliffs_delta([kr[c][g1] for c in case_ids],
                             [kr[c][g2] for c in case_ids])
        rows.append({
            "comparison": "%s>%s" % (g1, g2),
            "mean_paired_diff": round(sum(diffs) / len(diffs), 3),
            "bootstrap_percentile_ci95": [round(lo, 3), round(hi, 3)],
            "bootstrap_B": BOOT_B, "bootstrap_seed": BOOT_SEED,
            "wilcoxon": w,
            "cliffs_delta": round(delta, 3),
            "_diffs": diffs, "_a": [kr[c][g1] for c in case_ids],
            "_b": [kr[c][g2] for c in case_ids],
        })
    adj = holm([r["wilcoxon"]["p_normal_one_sided"] for r in rows])
    for r, pa in zip(rows, adj):
        r["holm_adjusted_p"] = round(pa, 3)
        r["wilcoxon"]["p_normal_one_sided"] = round(
            r["wilcoxon"]["p_normal_one_sided"], 4)
        r["wilcoxon"]["p_exact_sign_flip_rank"] = round(
            r["wilcoxon"]["p_exact_sign_flip_rank"], 5)
    return rows


def derive():
    with open(PERCASE) as f:
        pc = json.load(f)
    cases = pc["cases"]
    case_ids = sorted(cases)
    checks = []

    def check(label, got, want):
        ok = got == want
        checks.append({"check": label, "derived": got, "paper": want,
                       "pass": ok})
        return ok

    # --- group totals + Wilson ---
    n_total = sum(cases[c]["n_applied"] for c in case_ids)
    kills = {g: sum(cases[c]["kills"][g] for c in case_ids) for g in GROUPS}
    wilson_ci = {g: wilson(kills[g], n_total) for g in GROUPS}
    check("n_cases", len(case_ids), PAPER["n_cases"])
    check("denominator", n_total, PAPER["denominator"])
    for g in GROUPS:
        check("kills[%s]" % g, kills[g], PAPER["kills"][g])
        check("rate[%s]" % g, wilson_ci[g]["rate"], PAPER["rates"][g])
    check("T1 Wilson CI", wilson_ci["T1"]["ci95"], PAPER["t1_wilson"])

    # --- pre-registered paired family ---
    family = paired_family(cases, case_ids)
    t1b1 = family[0]
    check("mean paired diff T1-B1", t1b1["mean_paired_diff"],
          PAPER["mean_paired_diff"])
    check("bootstrap CI T1-B1", t1b1["bootstrap_percentile_ci95"],
          PAPER["boot_ci"])
    check("Holm p T1>B1", t1b1["holm_adjusted_p"], PAPER["holm_p"])
    check("Cliff's delta T1-B1", t1b1["cliffs_delta"],
          PAPER["cliffs_delta"])
    other_ns = all(r["holm_adjusted_p"] >= 0.05 for r in family[1:])
    checks.append({"check": "T1>A1 and B1>B2 not significant after Holm",
                   "derived": [r["holm_adjusted_p"] for r in family[1:]],
                   "paper": ">=0.05 (reported not significant)",
                   "pass": other_ns})

    # --- strengthening battery on T1>B1 (same estimand) ---
    diffs = t1b1["_diffs"]
    mc_p = signflip_mean_p(diffs)
    bca_lo, bca_hi = bca_delta_ci(t1b1["_a"], t1b1["_b"])
    battery = {
        "estimand": "one-sided case-level T1>B1 paired contrast "
                    "(identical to the pre-registered Holm-family member)",
        "exact_sign_flip_permutation_on_rank_statistic": {
            "method": "full 2^n_eff sign-flip null of Wilcoxon W+ via DP "
                      "over tie-averaged ranks scaled x2 (exact enumeration, "
                      "not sampled)",
            "n_eff_nonzero_diffs": t1b1["wilcoxon"]["n_eff"],
            "p_one_sided": t1b1["wilcoxon"]["p_exact_sign_flip_rank"],
        },
        "monte_carlo_sign_flip_on_mean_diff": {
            "method": "Monte Carlo sign-flip of the 34 paired differences, "
                      "statistic = mean; add-one convention (r+1)/(B+1)",
            "B": BOOT_B, "seed": BOOT_SEED, "p_one_sided": round(mc_p, 5),
        },
        "bca_bootstrap_ci_cliffs_delta": {
            "method": "paired case-resampling BCa (jackknife acceleration)",
            "B": BOOT_B, "seed": BOOT_SEED,
            "ci95": [round(bca_lo, 3), round(bca_hi, 3)],
            "excludes_zero": bca_lo > 0,
        },
        "wilcoxon_summary_statistics": {
            "V_wplus": t1b1["wilcoxon"]["V_wplus"],
            "z": t1b1["wilcoxon"]["z"],
            "p_unadjusted_one_sided": t1b1["wilcoxon"]["p_normal_one_sided"],
            "holm_adjusted_p": t1b1["holm_adjusted_p"],
        },
    }

    # --- sensitivity rerun (excl E-SUNDIALS-005), per the paper's claim ---
    sens_ids = [c for c in case_ids if c != SENS_EXCLUDE]
    sens = paired_family(cases, sens_ids)
    checks.append({"check": "sensitivity excl %s leaves T1>B1 Holm verdict "
                            "unchanged (<0.05)" % SENS_EXCLUDE,
                   "derived": sens[0]["holm_adjusted_p"],
                   "paper": "significant (verdict unchanged)",
                   "pass": sens[0]["holm_adjusted_p"] < 0.05})

    # --- real-defect face ---
    face = {c: cases[c]["face"] for c in case_ids}
    t1_detect = sum(1 for f in face.values() if f["t1"] == "DETECT")
    b1_miss = sum(1 for f in face.values() if f["b1"] == 0)
    b2_miss = sum(1 for f in face.values() if f["b2"] == 0)
    a1a_lose = sum(1 for f in face.values() if f["a1a"] == "LOSE")
    a1b_lose = sum(1 for f in face.values() if f["a1b"] == "LOSE")
    shared = sum(1 for f in face.values()
                 if f["a1a"] == "LOSE" and f["a1b"] == "LOSE")
    check("face T1 detect", t1_detect, PAPER["face_t1"])
    check("face B1 zero-detect (miss) cases", b1_miss, PAPER["face_b1_miss"])
    check("face B2 zero-detect (miss) cases", b2_miss, PAPER["face_b2_miss"])
    check("face A1-a (dimension-reduction) LOSE", a1a_lose,
          PAPER["face_a1a_lose"])
    check("face A1-b (de-strictification) LOSE", a1b_lose,
          PAPER["face_a1b_lose"])
    check("face shared (both-ablation) losses", shared,
          PAPER["face_shared_lose"])

    all_pass = all(c["pass"] for c in checks)

    for r in family + sens:
        for k in ("_diffs", "_a", "_b"):
            r.pop(k, None)

    arm = {
        "artefact": "industrial_arm_v1",
        "arm": "RQ4 industrial real-defect validation (Defect4MR)",
        "generated_by": "scripts/build_industrial_ssot.py (derive mode)",
        "derives_from": "data/results/industrial_percase_v1.json",
        "provenance": pc["provenance"],
        "census": {"n_cases": len(case_ids),
                   "denominator_all_mutant": n_total},
        "group_kill_totals": kills,
        "group_kill_rates_wilson95": wilson_ci,
        "preregistered_paired_family": family,
        "real_defect_face_totals": {
            "T1_detect": t1_detect,
            "B1_zero_detect_cases": b1_miss,
            "B1_nonzero_detect_cases": len(case_ids) - b1_miss,
            "B2_zero_detect_cases": b2_miss,
            "B2_nonzero_detect_cases": len(case_ids) - b2_miss,
            "A1a_dimension_reduction_lose": a1a_lose,
            "A1b_destrictification_lose": a1b_lose,
            "shared_losses": shared,
            "note": "T1 34/34 is selection-conditioned (case admission "
                    "requires T1-detectability); evidential content is the "
                    "contrast on the same admitted cases.",
        },
        "non_nesting_cases": ["A-LAPACK-004", "A-OPENBLAS-001",
                              "B-POCKETFFT-002", "E-ORDINARYDIFFEQ-001"],
        "verification_vs_paper": checks,
        "all_checks_pass": all_pass,
    }
    stats = {
        "artefact": "industrial_stats_v1",
        "generated_by": "scripts/build_industrial_ssot.py (derive mode)",
        "derives_from": "data/results/industrial_percase_v1.json",
        "bootstrap_B": BOOT_B, "bootstrap_seed": BOOT_SEED,
        "primary_comparison_T1_gt_B1": family[0],
        "R3_strengthening_battery": battery,
        "sensitivity_excl_E_SUNDIALS_005": sens[0],
        "full_family_sensitivity": sens,
        "verification_vs_paper": checks,
        "all_checks_pass": all_pass,
    }
    with open(os.path.join(RESULTS_DIR, "industrial_arm_v1.json"), "w") as f:
        json.dump(arm, f, indent=2)
        f.write("\n")
    with open(os.path.join(RESULTS_DIR, "industrial_stats_v1.json"),
              "w") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")

    print("=== industrial SSOT derivation vs paper ===")
    for c in checks:
        print(("  PASS " if c["pass"] else "  FAIL ")
              + "%s: derived=%s paper=%s" % (c["check"], c["derived"],
                                             c["paper"]))
    print("\n=== pre-registered family (all-mutant denominator) ===")
    for r in family:
        print("  %s: mean %+0.3f CI %s V=%.1f n_eff=%d z=%.3f "
              "p=%.4f Holm=%.3f delta=%+0.3f"
              % (r["comparison"], r["mean_paired_diff"],
                 r["bootstrap_percentile_ci95"], r["wilcoxon"]["V_wplus"],
                 r["wilcoxon"]["n_eff"], r["wilcoxon"]["z"],
                 r["wilcoxon"]["p_normal_one_sided"], r["holm_adjusted_p"],
                 r["cliffs_delta"]))
    print("\n=== strengthening battery (T1>B1) ===")
    print("  exact sign-flip permutation p (rank stat, 2^%d enumerated): %s"
          % (battery["exact_sign_flip_permutation_on_rank_statistic"]
             ["n_eff_nonzero_diffs"],
             battery["exact_sign_flip_permutation_on_rank_statistic"]
             ["p_one_sided"]))
    print("  Monte Carlo sign-flip p (mean stat, B=%d, seed %d): %s"
          % (BOOT_B, BOOT_SEED,
             battery["monte_carlo_sign_flip_on_mean_diff"]["p_one_sided"]))
    print("  BCa 95%% CI for Cliff's delta (B=%d, seed %d): %s"
          % (BOOT_B, BOOT_SEED,
             battery["bca_bootstrap_ci_cliffs_delta"]["ci95"]))
    print("  Wilcoxon V=%s z=%s unadjusted p=%s Holm p=%s"
          % (battery["wilcoxon_summary_statistics"]["V_wplus"],
             battery["wilcoxon_summary_statistics"]["z"],
             battery["wilcoxon_summary_statistics"]
             ["p_unadjusted_one_sided"],
             battery["wilcoxon_summary_statistics"]["holm_adjusted_p"]))
    print("  sensitivity excl %s: T1>B1 Holm=%.3f"
          % (SENS_EXCLUDE, sens[0]["holm_adjusted_p"]))
    print("\nall checks pass:", all_pass)
    print("wrote data/results/industrial_arm_v1.json")
    print("wrote data/results/industrial_stats_v1.json")
    return 0 if all_pass else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", metavar="DEPOSIT_ROOT",
                    help="extract per-case SSOT from a local Defect4MR "
                         "deposit copy")
    args = ap.parse_args()
    if args.extract:
        extract(args.extract)
        return 0
    if not os.path.exists(PERCASE):
        print("ERROR: %s missing; run --extract <deposit_root> first"
              % PERCASE, file=sys.stderr)
        return 2
    return derive()


if __name__ == "__main__":
    raise SystemExit(main())
