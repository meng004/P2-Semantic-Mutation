"""POST-HOC sensitivities for the Study-4 H4'''-graded pooled verdict.

NOT REGISTERED — both analyses respond to final-review findings R1-B1 and
R3-M1 and are clearly labelled post-hoc. The registered verdict in
h4_graded_v7.json is untouched.

S1 (admission-regime sensitivity, R1-B1): Study 3's v6 pools were built under
the P8-remediated all-family single-stratum screen; the v7 pools were not
(build_pools applies the screen to {v4,v5,v6} only). Approximate the screened
regime post hoc by restricting the graded aggregate to mutants whose flip
count fc == 1 (single-stratum killers) — the mutants the v6 admission gate
would have admitted. Under this restriction s_m in {0,1}: the share is the
fraction of single-stratum killers whose flip IS the declared primary.

S2 (cluster bootstrap, R3-M1): the registered unit-level bootstrap treats the
32 PUT-arm units as exchangeable although up to three units share a PUT.
Re-estimate the one-sided 95% lower bound by resampling the 15 distinct rich
PUTs with replacement, carrying each sampled PUT's full unit set.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from compute_h4_graded import (flip_map, load_matrix, _confirmatory_puts_present,
                               PILOT_PUTS, RICH_CLASSES, PRIMARY_CELLS_V3,
                               POOLED_GATE)

MATS = ["data/results/sms_track2_v7.json",
        "data/results/sms_track2_v7_same.json",
        "data/results/sms_track2_v7_recruit.json"]
SEED, B = 20260708, 10_000


def units(fc_max=None):
    """[(arm, put, mean_share, n_detected_mutants)] per detected rich PUT-arm."""
    out = []
    for path in MATS:
        matrix = load_matrix(ROOT / path)
        per_mutant, _ = flip_map(matrix, _confirmatory_puts_present(matrix))
        shares: dict = {}
        for (put, fname), (fc, fl, cat) in per_mutant.items():
            pl = put.lower()
            if pl in PILOT_PUTS or fc < 1 or pl[0] not in RICH_CLASSES:
                continue
            if fc_max is not None and fc > fc_max:
                continue
            s = (1.0 if PRIMARY_CELLS_V3[pl] in fl else 0.0) / fc
            shares.setdefault(put, []).append(s)
        for put, v in sorted(shares.items()):
            out.append((path, put, float(np.mean(v)), len(v)))
    return out


def lower95(means):
    rng = np.random.default_rng(SEED)
    boots = [float(np.mean(rng.choice(means, size=len(means), replace=True)))
             for _ in range(B)]
    return round(float(np.percentile(boots, 5)), 4)


def cluster_lower95(unit_rows):
    by_put: dict = {}
    for _, put, m, _n in unit_rows:
        by_put.setdefault(put, []).append(m)
    puts = sorted(by_put)
    rng = np.random.default_rng(SEED)
    boots = []
    for _ in range(B):
        sample = rng.choice(puts, size=len(puts), replace=True)
        vals = [m for p in sample for m in by_put[p]]
        boots.append(float(np.mean(vals)))
    return round(float(np.percentile(boots, 5)), 4), len(puts)


def main():
    reg = units()
    reg_means = [m for _, _, m, _ in reg]
    scr = units(fc_max=1)
    scr_means = [m for _, _, m, _ in scr]
    s2_lower, n_puts = cluster_lower95(reg)
    out = {
        "artefact": "h4_graded_v7_sensitivities",
        "status": "POST-HOC (NOT registered) — responds to final-review "
                  "findings R1-B1 (admission-regime change v6 screened vs v7 "
                  "unscreened) and R3-M1 (unit dependence across pools). The "
                  "registered verdict in h4_graded_v7.json is unchanged.",
        "inputs": MATS, "seed": SEED, "bootstrap_B": B,
        "registered_reference": {
            "pooled_n_rich": len(reg_means),
            "pooled_mean_share": round(float(np.mean(reg_means)), 4),
            "boot_lower_95_unit_level": lower95(reg_means)},
        "S1_screened_subset_fc1": {
            "definition": "graded aggregate restricted to fc==1 mutants "
                          "(post-hoc approximation of the v6 single-stratum "
                          "admission regime)",
            "n_rich_units_detected": len(scr_means),
            "recruitment_gate_24_met": len(scr_means) >= POOLED_GATE,
            "pooled_mean_share": (round(float(np.mean(scr_means)), 4)
                                  if scr_means else None),
            "boot_lower_95": lower95(scr_means) if scr_means else None,
            "units": [{"arm": Path(a).name, "put": p, "share": round(m, 4),
                       "n_mutants": n} for a, p, m, n in scr]},
        "S2_put_cluster_bootstrap": {
            "definition": "resample the distinct rich PUTs (with replacement),"
                          " carry each sampled PUT's full unit set",
            "n_distinct_puts": n_puts,
            "boot_lower_95": s2_lower,
            "bar": 0.15, "clears_bar": s2_lower > 0.15},
    }
    dst = ROOT / "data/results/h4_graded_v7_sensitivities.json"
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in
                      ("registered_reference", "S2_put_cluster_bootstrap")},
                     indent=1))
    s1 = out["S1_screened_subset_fc1"]
    print("S1 screened-subset:", {k: s1[k] for k in
          ("n_rich_units_detected", "recruitment_gate_24_met",
           "pooled_mean_share", "boot_lower_95")})
    print("wrote", dst)


if __name__ == "__main__":
    main()
