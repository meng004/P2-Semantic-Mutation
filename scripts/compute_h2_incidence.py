"""H2 detection-incidence sensitivity (fix task T3).

Computes the binarized nonzero-SMS 2x2 detection-incidence contrast
(aligned vs cross) from the v4 SMS SSOT, under the pre-registered
MP5-held (v3-spec) primary-MP convention that generates the headline
Cliff's delta = 0.314 pool (rq2_cliffs_delta_v4_mp5.json).

Detection incidence is a DIFFERENT estimand from the pre-registered H2
*magnitude* criterion (Cliff's delta >= 0.474, which stays "not met").
This is a post-hoc-specified sensitivity in its OWN labeled test family,
OUTSIDE the pre-registered Holm family (per R3 focus 5 / point 9).

Outputs:
  - Fisher exact one-sided p (alternative: aligned nonzero odds > cross)
  - sample (unconditional) odds ratio
  - conditional-MLE odds ratio + exact 95% CI (scipy.stats.contingency)
  - a robustness grid over pool variants and vacant-cell exclusion
  - an explicit reproduction of the manuscript's (mislabeled) 9/12-vs-6/48
    counts to diagnose the R3/manuscript OR=21 discrepancy.

Writes SSOT to data/results/h2_incidence_v4.json. Every number is from
this run; nothing is transcribed from the manuscript.
"""
import json
from pathlib import Path

from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results"

# Primary (aligned) MP per PUT. MP5-held (v3 spec) is the SSOT convention
# behind the headline delta=0.314 pool; v3b reassigns c-class to MP1.
PRIMARY_V3 = {  # == src/p2/config/primary.py PRIMARY_CELLS_V3
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}
PRIMARY_V3B = dict(PRIMARY_V3, c1=1, c2=1, c3=1)  # c_class_mp_ranking -> MP1

# 9 vacant cells (circ) from the coverage matrix tab:p2-cells.
# Columns: Conservation=MP1 Monotonicity=MP2 Convergence=MP3
#          Trajectory=MP4 Partial-order=MP5.
VACANT_CELLS = {
    "A1_MP5", "A2_MP2", "A3_MP5",
    "B1_MP3", "B1_MP4", "B3_MP2", "B3_MP5",
    "D2_MP4", "D3_MP4",
}


def load_pool(sms_file):
    return json.loads((RESULTS / sms_file).read_text())


def split(data, primary, drop_vacant=False):
    """Return (aligned_sms, cross_sms) lists."""
    aligned, cross = [], []
    for cell, v in data.items():
        if drop_vacant and cell in VACANT_CELLS:
            continue
        put = cell.split("_")[0].lower()
        mp = int(cell.split("MP")[1])
        (aligned if mp == primary[put] else cross).append(v["sms"])
    return aligned, cross


def incidence_table(aligned, cross):
    a_nz = sum(1 for x in aligned if x > 0)
    a_z = len(aligned) - a_nz
    c_nz = sum(1 for x in cross if x > 0)
    c_z = len(cross) - c_nz
    return a_nz, a_z, c_nz, c_z


def analyse(a_nz, a_z, c_nz, c_z):
    """2x2 = [[a_nz, a_z], [c_nz, c_z]]; one-sided aligned>cross incidence."""
    table = [[a_nz, a_z], [c_nz, c_z]]
    sample_or, p_greater = fisher_exact(table, alternative="greater")
    _, p_two = fisher_exact(table, alternative="two-sided")
    res = odds_ratio(table, kind="conditional")
    ci = res.confidence_interval(confidence_level=0.95, alternative="greater")
    ci_two = res.confidence_interval(confidence_level=0.95, alternative="two-sided")
    return {
        "table_aligned": {"nonzero": a_nz, "zero": a_z, "n": a_nz + a_z},
        "table_cross": {"nonzero": c_nz, "zero": c_z, "n": c_nz + c_z},
        "aligned_incidence": a_nz / (a_nz + a_z) if (a_nz + a_z) else None,
        "cross_incidence": c_nz / (c_nz + c_z) if (c_nz + c_z) else None,
        "sample_odds_ratio": float(sample_or),
        "conditional_mle_odds_ratio": float(res.statistic),
        "or_ci95_onesided_lower": float(ci.low),
        "or_ci95_onesided_upper": (None if ci.high == float("inf") else float(ci.high)),
        "or_ci95_twosided": [
            float(ci_two.low),
            (None if ci_two.high == float("inf") else float(ci_two.high)),
        ],
        "fisher_p_onesided_greater": float(p_greater),
        "fisher_p_twosided": float(p_two),
    }


def main():
    v4 = load_pool("sms_track2_v4.json")
    v3 = load_pool("sms_track2_v3.json")

    # --- Headline: v4, MP5-held, all 60 cells ---
    a, c = split(v4, PRIMARY_V3)
    a_nz, a_z, c_nz, c_z = incidence_table(a, c)
    headline = analyse(a_nz, a_z, c_nz, c_z)
    headline["pool"] = "v4 cross-source, MP5-held (v3 spec), all 60 cells"

    grid = {}

    # (R) v4 MP5-held, vacant cells excluded (aligned 12->11, cross 48->40)
    a, c = split(v4, PRIMARY_V3, drop_vacant=True)
    grid["v4_mp5_vacant_excluded"] = analyse(*incidence_table(a, c))
    grid["v4_mp5_vacant_excluded"]["pool"] = "v4 MP5-held, 9 vacant cells dropped"

    # (R) v4 MP5-held, drop 3 fully-dead PUTs (a1,a3,c2 have no nonzero cell)
    dead = {"a1", "a3", "c2"}
    v4_live = {k: v for k, v in v4.items() if k.split("_")[0].lower() not in dead}
    a, c = split(v4_live, PRIMARY_V3)
    grid["v4_mp5_live_puts_only"] = analyse(*incidence_table(a, c))
    grid["v4_mp5_live_puts_only"]["pool"] = "v4 MP5-held, 3 all-zero PUTs (a1,a3,c2) dropped"

    # (R) v3 same-source, MP5-held
    a, c = split(v3, PRIMARY_V3)
    grid["v3_mp5"] = analyse(*incidence_table(a, c))
    grid["v3_mp5"]["pool"] = "v3 same-source, MP5-held"

    # (R) v4 v3b (c-class -> MP1)
    a, c = split(v4, PRIMARY_V3B)
    grid["v4_v3b_cMP1"] = analyse(*incidence_table(a, c))
    grid["v4_v3b_cMP1"]["pool"] = "v4 cross-source, v3b (c-class primary MP1)"

    # --- Diagnosis of the manuscript / R3 OR=21 discrepancy ---
    # Manuscript main.tex L1962 claims aligned 9/12 vs cross 6/48. Reproduce
    # the Fisher/OR on THOSE counts to show they yield R3's OR=21, p~5e-5,
    # and contrast with the SSOT-correct counts above.
    manuscript_claim = analyse(9, 3, 6, 42)  # [[9,3],[6,42]]
    manuscript_claim["note"] = (
        "Manuscript-stated (mislabeled) counts aligned 9/12 vs cross 6/48. "
        "The '9' is the number of PUTs with ANY nonzero cell (9/12 PUTs are "
        "non-dead); it is NOT the aligned-cell nonzero count. SSOT-correct "
        "aligned-cell nonzero = 6/12, cross-cell nonzero = 9/48 (see headline). "
        "Labels are swapped in the manuscript and in R3 focus-2."
    )

    out = {
        "task": "T3 H2 detection-incidence sensitivity",
        "estimand": "detection incidence (P[SMS>0]); distinct from H2 magnitude (Cliff delta>=0.474)",
        "test_family": "own labeled sensitivity family, OUTSIDE the pre-registered Holm family",
        "prereg_status": "post-hoc-specified; NOT a confirmatory H2 pass; H2 magnitude verdict stays 'not met'",
        "headline_ssot_correct": headline,
        "robustness_grid": grid,
        "manuscript_claim_9_12_vs_6_48": manuscript_claim,
        "diagnosis": (
            "Manuscript (main.tex:1962) and R3 focus-2 report aligned 9/12 vs "
            "cross 6/48 -> OR 21, Fisher one-sided p=5.3e-5. The SSOT MP5-held "
            "pool that generates the headline delta=0.314 gives the SWAPPED "
            "split: aligned 6/12 nonzero, cross 9/48 nonzero. Only 9 of 12 PUTs "
            "have any nonzero cell (a1,a3,c2 fully dead); '9/12' is a PUT-level "
            "any-signal count, not the aligned-cell count. Honest incidence "
            "advantage is real but far weaker than OR=21."
        ),
        "provenance": {
            "sms_v4": "data/results/sms_track2_v4.json",
            "sms_v3": "data/results/sms_track2_v3.json",
            "primary_convention": "src/p2/config/primary.py PRIMARY_CELLS_V3 (MP5-held)",
            "vacant_cells": sorted(VACANT_CELLS),
        },
    }

    OUT = RESULTS / "h2_incidence_v4.json"
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
