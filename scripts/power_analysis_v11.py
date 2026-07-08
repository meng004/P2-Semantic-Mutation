"""Study-2 pre-registration AMENDMENT v1.1 power / feasibility analysis.

Adds a-priori feasibility/power analyses for the THREE successor hypotheses
H1' (instantiability), H3' (class-consistency), H4' (attribution) that the v1.0
registration (docs/prereg_v2/PREREGISTRATION_STUDY2.md) carried only as naive
Study-1-threshold carry-forwards (H2-5/6/7). Every registered threshold in
PREREGISTRATION_STUDY2_v1.1.md traces to the JSON this script writes to
data/results/power_study2_v11.json.

It ALSO recomputes the two SMS legs (H2-1' aligned>cross, H2-2 source-diversity
Delta-delta) at the pilot-adjusted confirmatory n = 28 (30 PUTs minus the two
calibration-pilot PUTs a2 + b4), reusing the v1.0 methodology verbatim by
importing scripts/power_analysis_study2.py.

Integrity: NO LLM / API calls, NO Study-2 mutant data. Pure resampling from the
committed Study-1 SSOTs (sms_track2_v4.json, s5_purity_v4.json) plus the
operator registry (src/p2/mutators/operator_registry.py), which was authored
BLIND to mutation outcomes, so operator->PUT coverage is an outcome-independent
property of the spec.

Master seed 20260708 (v1.1 amendment keeps the v1.0 freeze-date seed convention).

Usage:
    PYTHONPATH=src python3 scripts/power_analysis_v11.py
"""
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data" / "results"
OUT = RESULTS / "power_study2_v11.json"

MASTER_SEED = 20260708
N_SIM = 20000
ALPHA = 0.05

# Calibration-pilot PUTs (excluded from every confirmatory count; item 2).
PILOT_PUTS = ("a2", "b4")

# The five operator families reported in Study-1 H1 (main.tex Table tab:p2-32).
# CF is a 6th, minor family (only b2, a8); it is NOT one of the H1 "5 families",
# so it does not enter the H1' "X of 5" count (kept identical to Study-1 shape).
H1_FAMILIES = ("CE", "OS", "HP", "TF", "SI")

# Study-1 applicability-adjusted per-family success rate = fraction of APPLICABLE
# PUTs on which the family produced >=5 non-equivalent mutants
# (main.tex L2063: "CE 4/8, OS 5/7, HP 9/9, TF 5/6, SI 1/6"). These are the
# outcome-calibrated per-applicable-PUT success probabilities for the H1' DGP.
STUDY1_APPLICABLE = {"CE": (4, 8), "OS": (5, 7), "HP": (9, 9), "TF": (5, 6), "SI": (1, 6)}


# ---------------------------------------------------------------------------
# Reuse v1.0 methodology by importing scripts/power_analysis_study2.py
# ---------------------------------------------------------------------------
def _load_v10_module():
    spec = importlib.util.spec_from_file_location(
        "power_analysis_study2", ROOT / "scripts" / "power_analysis_study2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Operator -> PUT coverage (outcome-independent; from the blind-authored registry)
# ---------------------------------------------------------------------------
def family_coverage():
    from p2.mutators.operator_registry import OPERATORS
    by_put_cat = defaultdict(set)
    for op in OPERATORS:
        by_put_cat[op.put].add(op.category)
    all_puts = sorted(by_put_cat)  # a1..d8 = 30
    conf_puts = [p for p in all_puts if p not in PILOT_PUTS]  # 28
    cov_all, cov_conf = {}, {}
    for fam in H1_FAMILIES:
        cov_all[fam] = sum(1 for p in all_puts if fam in by_put_cat[p])
        cov_conf[fam] = sum(1 for p in conf_puts if fam in by_put_cat[p])
    return {
        "n_puts_total": len(all_puts),
        "n_puts_confirmatory": len(conf_puts),
        "confirmatory_puts": conf_puts,
        "coverage_all30": cov_all,
        "coverage_confirmatory28": cov_conf,
    }


# ---------------------------------------------------------------------------
# H1' — instantiability feasibility on the ACTUAL 30-PUT x 91-op coverage
# ---------------------------------------------------------------------------
def power_h1_instantiability(cov):
    """Feasibility Monte-Carlo. Per family f, of its coverage_conf[f] applicable
    confirmatory PUTs, each independently yields >=5 non-equivalent mutants with
    the Study-1-calibrated per-applicable success probability (Jeffreys-shrunk to
    avoid a degenerate p=1 for HP). Registered criterion (same shape as Study-1
    H1): >=X of 5 families produce >=5 non-equiv mutants on >=M of 28 confirmatory
    PUTs. We sweep M and register the largest (X=4, M) with feasibility >=0.80."""
    rng = np.random.default_rng(MASTER_SEED + 11)
    cov_conf = cov["coverage_confirmatory28"]
    # Jeffreys point estimate (k+0.5)/(n+1): honest small-sample shrinkage.
    rate = {f: (k + 0.5) / (n + 1) for f, (k, n) in STUDY1_APPLICABLE.items()}
    raw_rate = {f: k / n for f, (k, n) in STUDY1_APPLICABLE.items()}
    expected = {f: round(cov_conf[f] * rate[f], 3) for f in H1_FAMILIES}

    # Monte-Carlo achieved counts per family.
    achieved = {f: rng.binomial(cov_conf[f], rate[f], size=N_SIM) for f in H1_FAMILIES}
    per_family_ge = {}   # P(family clears >=M) for M in 1..12
    for f in H1_FAMILIES:
        per_family_ge[f] = {M: float((achieved[f] >= M).mean()) for M in range(1, 13)}

    stack = np.stack([achieved[f] for f in H1_FAMILIES], axis=0)  # (5, N_SIM)
    feasible_4of5 = {}
    for M in range(1, 13):
        n_clear = (stack >= M).sum(axis=0)  # families clearing M per sim
        feasible_4of5[M] = float((n_clear >= 4).mean())
    ok = [M for M in range(1, 13) if feasible_4of5[M] >= 0.80]
    registered_M = max(ok) if ok else None
    return {
        "criterion_shape": ">=4 of 5 operator families produce >=5 non-equivalent "
                           "mutants on >=M of 28 confirmatory PUTs",
        "coverage_ceiling_confirmatory28": cov_conf,
        "study1_per_applicable_success_raw": {f: round(raw_rate[f], 4) for f in H1_FAMILIES},
        "per_family_success_rate_jeffreys": {f: round(rate[f], 4) for f in H1_FAMILIES},
        "expected_puts_cleared_per_family": expected,
        "per_family_P_clear_M": per_family_ge,
        "feasibility_P_ge4of5_clear_M": feasible_4of5,
        "registered_X": 4,
        "registered_M": registered_M,
        "registered_feasibility": (feasible_4of5[registered_M] if registered_M else None),
        "note": "SI (narrow high-risk family, Study-1 1/6) is expected to stay "
                "below the bar, as in Study 1; the other four clear >=M.",
    }


# ---------------------------------------------------------------------------
# H3' — class-level direction consistency power
# ---------------------------------------------------------------------------
def power_h3_class_consistency(dgp, cov):
    """Per-class direction consistency under the Study-1-calibrated hurdle DGP.
    Confirmatory class sizes (28 PUTs, pilots a2,b4 removed): A=7, B=6, C=7, D=8.
    Per PUT i: aligned cell a_i ~ hurdle(p_a, mags_a); cross representative
    c_i = mean of 4 cross cells ~ hurdle(p_c, mags_c). Class is 'positive' if the
    class-mean aligned exceeds class-mean cross. Registered criterion: positive
    direction in >=3 of 4 classes. Also reports the per-class one-sided sign-test
    power (binomial on within-class per-PUT signs) as the descriptive companion."""
    rng = np.random.default_rng(MASTER_SEED + 13)
    conf = cov["confirmatory_puts"]
    class_sizes = {cl: sum(1 for p in conf if p[0] == cl) for cl in "abcd"}
    p_a, mags_a = dgp["p_nonzero_aligned"], dgp["aligned_nonzero_mag"]
    p_c, mags_c = dgp["p_nonzero_cross"], dgp["cross_nonzero_mag"]

    def draw_hurdle(n, p, mags):
        nz = rng.random(n) < p
        out = np.zeros(n)
        k = int(nz.sum())
        if k:
            out[nz] = rng.choice(mags, size=k, replace=True)
        return out

    n_pos_classes = np.zeros(N_SIM, dtype=int)
    signtest_hits = {cl: 0 for cl in "abcd"}
    for s in range(N_SIM):
        pos_this = 0
        for cl, nc in class_sizes.items():
            a = draw_hurdle(nc, p_a, mags_a)
            c = np.array([draw_hurdle(4, p_c, mags_c).mean() for _ in range(nc)])
            if a.mean() > c.mean():
                pos_this += 1
            d = a - c
            npos, nneg = int((d > 0).sum()), int((d < 0).sum())
            nn = npos + nneg
            if nn:
                # one-sided binomial: H0 p=0.5, alt positive median
                pval = stats.binomtest(npos, nn, 0.5, alternative="greater").pvalue
                if pval < ALPHA:
                    signtest_hits[cl] += 1
        n_pos_classes[s] = pos_this
    return {
        "criterion": ">=3 of 4 classes show positive class-level aligned>cross direction",
        "confirmatory_class_sizes": class_sizes,
        "power_P_ge3of4_positive": float((n_pos_classes >= 3).mean()),
        "power_P_4of4_positive": float((n_pos_classes == 4).mean()),
        "per_class_signtest_power": {cl: signtest_hits[cl] / N_SIM for cl in "abcd"},
        "note": "The confirmatory criterion is the >=3/4 direction-consistency test "
                "(powered >=0.8 below). Per-class binomial sign tests are "
                "under-powered at 6-8 PUTs/class (many SMS ties) and are reported "
                "descriptively; Friedman chi^2 stays exploratory as in Study 1.",
    }


# ---------------------------------------------------------------------------
# H4' — attribution: expected post-constraint suspect_share (single-stratum spec)
# ---------------------------------------------------------------------------
def power_h4_attribution():
    """Derive the residual expected leakage under the single-stratum spec
    constraint (sibling amendment item). In Study 1 (s5_purity_v4.json) all 29
    multi-stratum mutants came from CF (9) + TF (20). The already-single-stratum
    families CE/OS/HP/SI show ZERO incidental multi-stratum leakage. Under a
    single-stratum re-spec of CF/TF, the residual incidental leakage is projected
    at the observed single-stratum-family rate (0/N), whose one-sided 95% upper
    bound is the rule-of-three 3/N. Register the suspect_share threshold with a
    stated margin above that bound."""
    s5 = json.loads((RESULTS / "s5_purity_v4.json").read_text())
    per_op = s5["per_operator"]
    total_mut = s5["overall"]["n_mutants"]
    total_multi = s5["overall"]["n_multistratum_flip_ge2"]
    # multi-stratum by family
    multi_by_fam = {f: per_op[f]["n_multistratum"] for f in per_op}
    single_fams = [f for f in per_op if f not in ("CF", "TF")]  # already single-stratum
    n_single = sum(per_op[f]["n_mutants"] for f in single_fams)
    multi_single = sum(per_op[f]["n_multistratum"] for f in single_fams)
    # rule-of-three one-sided 95% upper bound for a 0/N observation
    rule_of_three = 3.0 / n_single if multi_single == 0 else None
    projected_upper = rule_of_three
    registered_threshold = 0.05
    margin = round(registered_threshold - projected_upper, 4)
    return {
        "metric": "mean suspect_share (LRCA multi-stratum leakage) over the 140 "
                  "confirmatory cells (28 PUTs x 5 MP); LRCA machinery identical to Study 1",
        "study1_multistratum_total": total_multi,
        "study1_n_mutants": total_mut,
        "study1_overall_multistratum_fraction": round(total_multi / total_mut, 4),
        "study1_multistratum_by_family": multi_by_fam,
        "study1_multistratum_from_CF_TF": multi_by_fam.get("CF", 0) + multi_by_fam.get("TF", 0),
        "single_stratum_families": single_fams,
        "single_stratum_family_n_mutants": n_single,
        "single_stratum_family_multistratum": multi_single,
        "single_stratum_leakage_rate": multi_single / n_single,
        "projected_post_constraint_upper_95_rule_of_three": round(projected_upper, 4),
        "registered_threshold": registered_threshold,
        "margin_above_projected_upper": margin,
        "note": "CF+TF supplied 29/29 multi-stratum mutants in Study 1; a "
                "single-stratum re-spec pushes their incidental leakage to the "
                "CE/OS/HP/SI regime (0/%d observed). Threshold 0.05 sits %.3f above "
                "the rule-of-three upper bound." % (n_single, margin),
    }


def main():
    v10 = _load_v10_module()
    dgp = v10.load_study1_sms_hurdle()
    cov = family_coverage()

    # SMS legs re-evaluated at pilot-adjusted n=28 (plus the v1.0 grid for lineage)
    grid = (12, 18, 24, 28, 30, 36)
    a28 = v10.power_cliffs(dgp, n_puts=grid, thresholds=(0.0, 0.147, 0.330))
    b28 = v10.power_delta_delta(dgp, n_puts=grid, delta_deltas=(0.10, 0.15, 0.20))

    result = {
        "meta": {
            "purpose": "Study-2 pre-registration AMENDMENT v1.1 power/feasibility "
                       "analysis; frozen before any Study-2 data generation.",
            "amends": "data/results/power_study2.json (v1.0)",
            "master_seed": MASTER_SEED, "n_sim": N_SIM, "alpha": ALPHA,
            "dgp_source": "data/results/sms_track2_v4.json (MP5-held pool)",
            "leakage_source": "data/results/s5_purity_v4.json",
            "coverage_source": "src/p2/mutators/operator_registry.py (blind-authored spec)",
            "pilot_puts_excluded": list(PILOT_PUTS),
            "numpy": np.__version__, "scipy": scipy.__version__,
        },
        "coverage": cov,
        "h1_instantiability": power_h1_instantiability(cov),
        "h3_class_consistency": power_h3_class_consistency(dgp, cov),
        "h4_attribution": power_h4_attribution(),
        "sms_legs_pilot_adjusted_n28": {
            "note": "Confirmatory n drops 30->28 after removing the two pilot PUTs; "
                    "these recompute H2-1' (delta>0) and H2-2 (Delta-delta) power at n=28.",
            "a_cliffs_delta_power": a28,
            "b_dual_blind_delta_delta": b28,
        },
    }
    OUT.write_text(json.dumps(result, indent=2))
    print("wrote", OUT.relative_to(ROOT))

    h1 = result["h1_instantiability"]
    print("\n[H1'] coverage(28) =", h1["coverage_ceiling_confirmatory28"])
    print("      expected cleared =", h1["expected_puts_cleared_per_family"])
    print("      registered: >=%d of 5 families clear >=%d/28  feasibility=%.3f"
          % (h1["registered_X"], h1["registered_M"], h1["registered_feasibility"]))
    h3 = result["h3_class_consistency"]
    print("[H3'] class sizes =", h3["confirmatory_class_sizes"],
          " P(>=3/4 positive) =", round(h3["power_P_ge3of4_positive"], 3))
    h4 = result["h4_attribution"]
    print("[H4'] Study-1 multistratum %d/%d (CF+TF=%d); single-stratum leakage %d/%d; "
          "rule-of-three upper=%.4f; registered threshold=%.2f (margin %.4f)"
          % (h4["study1_multistratum_total"], h4["study1_n_mutants"],
             h4["study1_multistratum_from_CF_TF"], h4["single_stratum_family_multistratum"],
             h4["single_stratum_family_n_mutants"],
             h4["projected_post_constraint_upper_95_rule_of_three"],
             h4["registered_threshold"], h4["margin_above_projected_upper"]))
    print("[H2-1'] delta>0 power @n28 =", a28["power_by_threshold"]["delta_ref_0.0"][28])
    print("[H2-2]  Delta-delta=0.2 power @n28 =", b28["power"]["dd_0.2"][28])


if __name__ == "__main__":
    main()
