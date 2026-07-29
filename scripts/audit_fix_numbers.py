#!/usr/bin/env python3
"""Recompute every number corrected by the 2026-07-29 legacy-residue audit.

Single source of truth for the source/main.tex + source/supplementary.tex
repairs: MP5-primary slice statistics, H1 per-operator counts, H3 per-class
deltas, H4 estimand readings under the NA convention, the v3 unresolved
census, the exactness-defect xi audit, PUT LOC, and the coverage-matrix
partition. Writes data/results/audit_fix_numbers.json and
data/results/xi_exactness_defect_v4.json.
"""
from __future__ import annotations

import json
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data/results"
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY  # noqa: E402
from p2.stats.tosem_revision import (  # noqa: E402
    gap_premise_support,
    summarize_lrca,
)

# operator category -> targeted stratum / meta-pattern index
CAT2MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}
CAT_RE = re.compile(r"_(CE|OS|HP|TF|SI|CF)\d")


def load(name):
    return json.loads((RES / name).read_text())


def cell_key(cell):
    put = cell.split("_")[0].lower()
    mp = int(cell.split("MP")[1])
    return put, mp


def slice_stats(sms):
    aligned, cross = [], []
    for cell, v in sms.items():
        put, mp = cell_key(cell)
        (aligned if mp == PRIMARY[put] else cross).append(v["sms"])
    out = {
        "n_aligned": len(aligned), "n_cross": len(cross),
        "mean_aligned": round(st.mean(aligned), 4),
        "mean_cross": round(st.mean(cross), 4),
        "median_aligned": round(st.median(aligned), 4),
        "median_cross": round(st.median(cross), 4),
        "zero_aligned": sum(1 for s in aligned if s == 0),
        "zero_cross": sum(1 for s in cross if s == 0),
        "nonzero_aligned": sum(1 for s in aligned if s > 0),
        "nonzero_cross": sum(1 for s in cross if s > 0),
    }
    a1, a0 = out["nonzero_aligned"], out["zero_aligned"]
    c1, c0 = out["nonzero_cross"], out["zero_cross"]
    out["binarized_or"] = round((a1 / a0) / (c1 / c0), 2) if a0 and c0 and c1 else None
    return out


def per_class_delta(sms):
    per = {}
    for c in "abcd":
        al = [v["sms"] for cell, v in sms.items()
              if cell_key(cell)[0].startswith(c) and cell_key(cell)[1] == PRIMARY[cell_key(cell)[0]]]
        cr = [v["sms"] for cell, v in sms.items()
              if cell_key(cell)[0].startswith(c) and cell_key(cell)[1] != PRIMARY[cell_key(cell)[0]]]
        per[c] = round(st.mean(al) - st.mean(cr), 4)
    vals = list(per.values())
    cv = st.stdev(vals) / abs(st.mean(vals))
    return {"delta_sms": per, "sign_positive": sum(1 for v in vals if v > 0),
            "inverted_classes": [c for c, v in per.items() if v <= 0],
            "cv_sample": round(cv, 3)}


def class_means(sms):
    out = {}
    for c in "abcd":
        vals = [v["sms"] for cell, v in sms.items() if cell_key(cell)[0].startswith(c)]
        out[c] = round(st.mean(vals), 4)
    return out


def h1_counts(sms):
    """Confirmed non-equivalent mutants per (PUT, operator category).

    v4: equiv == 0 in every cell, so the admitted pool is the confirmed
    non-equivalent universe. Pool composition read from any one cell per PUT
    (the same per-PUT pool is reused across the five MPs).
    """
    per_put_cat = {}
    for cell, v in sms.items():
        put, mp = cell_key(cell)
        if mp != 1:
            continue
        assert v["equiv"] == 0, f"unexpected equiv>0 in v4 cell {cell}"
        cats = {}
        for o in v["outcomes"]:
            m = CAT_RE.search(o["file"])
            cat = m.group(1) if m else "UNK"
            cats[cat] = cats.get(cat, 0) + 1
        per_put_cat[put] = cats
    table = {}
    for cat in ["CE", "OS", "HP", "TF", "SI", "CF"]:
        puts_ge5 = [p for p, cats in per_put_cat.items() if cats.get(cat, 0) >= 5]
        table[cat] = {"puts_ge5": len(puts_ge5), "puts": sorted(puts_ge5),
                      "per_put": {p: per_put_cat[p].get(cat, 0) for p in sorted(per_put_cat)}}
    ge5_main5 = [cat for cat in CAT2MP if table[cat]["puts_ge5"] >= 9]
    return {"per_operator": table, "operators_clearing_9put_bar": ge5_main5,
            "h1_pass_count": len(ge5_main5)}


def h4_readings(lrca):
    """H4 under the NA convention: zero-kill cells carry no defined suspect_share."""
    kill_cells, zero_cells = {}, []
    for cell, v in lrca.items():
        if v["n_killed"] > 0:
            kill_cells[cell] = v
        else:
            zero_cells.append(cell)
    suspect_kills = sum(v["n_killed"] - v["labels"]["C1_legit_fault"] for v in kill_cells.values())
    total_kills = sum(v["n_killed"] for v in kill_cells.values())
    shares = [v["suspect_share"] for v in kill_cells.values()]
    low = {c: v["suspect_share"] for c, v in kill_cells.items() if v["suspect_share"] <= 0.20}
    low_aligned = [c for c in low if cell_key(c)[1] == PRIMARY[cell_key(c)[0]]]
    sweep = {}
    for cut in [round(0.05 * i, 2) for i in range(1, 11)]:
        sweep[str(cut)] = sum(1 for s in shares if s <= cut)
    return {
        "_incl_L0_note": "incl-L0 readings treat LRCA L0-prescreened artefact kills as suspect over the SMS killed denominator",
        "cells_total": len(lrca), "cells_zero_kill_NA": len(zero_cells),
        "cells_evaluable": len(kill_cells),
        "macro_mean_kill_cells": round(st.mean(shares), 4),
        "median_kill_cells": round(st.median(shares), 4),
        "pooled_suspect_share": round(suspect_kills / total_kills, 4),
        "total_kills_lrca": total_kills, "suspect_kills": suspect_kills,
        "cells_le_020": len(low), "cells_le_020_aligned": len(low_aligned),
        "cells_le_020_cross": len(low) - len(low_aligned),
        "cutoff_sweep_evaluable": sweep,
        "legacy_invalid_mean_all60_do_not_use": round(
            st.mean([v["suspect_share"] for v in lrca.values()]), 4
        ),
    }


def v3_unresolved(sms3):
    cells = {c: v for c, v in sms3.items() if v["equiv"] > 0}
    return {
        "cells_with_equiv": len(cells), "equiv_incidences": sum(v["equiv"] for v in cells.values()),
        "all_zero_kill": all(v["killed"] == 0 for v in cells.values()),
        "cells": {c: {"equiv": v["equiv"], "killed": v["killed"]} for c, v in sorted(cells.items())},
    }


def xi_audit(sms):
    """Exactness defect xi: off-diagonal kill mass / total kills.

    Fiber label = generation-time operator category (provenance bridge);
    checker stratum = the cell's MP index. CF and unparseable categories are
    off-taxonomy and count as off-diagonal deviation mass.
    """
    per_cell, total_kills, offdiag_kills = {}, 0, 0
    diag_by_cat = {}
    for cell, v in sms.items():
        put, mp = cell_key(cell)
        kills = [o for o in v["outcomes"] if o["label"] == "KILLED"]
        off = 0
        for o in kills:
            m = CAT_RE.search(o["file"])
            cat = m.group(1) if m else "UNK"
            stratum = CAT2MP.get(cat)
            if stratum != mp:
                off += 1
            else:
                diag_by_cat[cat] = diag_by_cat.get(cat, 0) + 1
        n = len(kills)
        total_kills += n
        offdiag_kills += off
        per_cell[cell] = {"kills": n, "offdiag": off,
                          "xi": round(off / n, 4) if n else None,
                          "aligned": mp == PRIMARY[put]}
    evaluable = {c: v for c, v in per_cell.items() if v["xi"] is not None}
    aligned_eval = {c: v for c, v in evaluable.items() if v["aligned"]}
    cross_eval = {c: v for c, v in evaluable.items() if not v["aligned"]}
    def pooled(d):
        k = sum(v["kills"] for v in d.values()); o = sum(v["offdiag"] for v in d.values())
        return round(o / k, 4) if k else None
    return {
        "definition": "xi = block-off-diagonal kill mass / total kills; NA when total kills = 0",
        "fiber_source": "generation-time operator category (CE->1 OS->2 HP->3 TF->4 SI->5; CF/unparseable = off-taxonomy)",
        "total_kills": total_kills, "offdiag_kills": offdiag_kills,
        "xi_pooled": round(offdiag_kills / total_kills, 4),
        "cells_evaluable": len(evaluable), "cells_NA": 60 - len(evaluable),
        "xi_pooled_aligned_cells": pooled(aligned_eval),
        "xi_pooled_cross_cells": pooled(cross_eval),
        "diagonal_kills_by_category": diag_by_cat,
        "per_cell": per_cell,
    }


def loc_table():
    out = {}
    for f in sorted((ROOT / "src/p2/puts").glob("[a-d][0-9].py")):
        text = f.read_text().splitlines()
        out[f.stem] = {"loc": len(text), "bytes": f.stat().st_size}
    return out


def coverage_partition():
    grid = {
        "a1": "2 1 2 2 0", "a2": "2 0 1 1 2", "a3": "2 1 2 2 0",
        "b1": "2 1 0 0 1", "b2": "1 2 2 2 1", "b3": "2 0 2 1 0",
        "c1": "1 2 2 1 2", "c2": "2 1 2 1 2", "c3": "1 2 2 2 2",
        "d1": "2 2 1 1 2", "d2": "1 2 1 0 2", "d3": "2 2 1 0 2",
    }
    tot = {0: 0, 1: 0, 2: 0}
    aligned = {0: 0, 1: 0, 2: 0}
    cross = {0: 0, 1: 0, 2: 0}
    for put, row in grid.items():
        for mp, mark in enumerate(map(int, row.split()), start=1):
            tot[mark] += 1
            (aligned if mp == PRIMARY[put] else cross)[mark] += 1
    return {"substantial": tot[2], "moderate": tot[1], "vacant": tot[0],
            "aligned": {"substantial": aligned[2], "moderate": aligned[1], "vacant": aligned[0]},
            "cross": {"substantial": cross[2], "moderate": cross[1], "vacant": cross[0]}}


def h4_incl_l0(sms, lrca):
    tot_k = susp = 0
    macro, smsc1 = [], []
    for cell, v in sms.items():
        k, l = v["killed"], lrca[cell]
        c1 = l["labels"]["C1_legit_fault"]
        tot_k += k
        susp += k - c1
        if k > 0:
            macro.append((k - c1) / k)
        smsc1.append(v["sms"] * l["c1_share"])
    return {"pooled_incl_L0": round(susp / tot_k, 4), "suspect_incl_L0": susp,
            "total_kills_sms": tot_k, "macro_incl_L0_kill_cells": round(st.mean(macro), 4),
            "mean_sms_c1_60cells": round(st.mean(smsc1), 4),
            "nonzero_sms_c1_cells": sum(1 for x in smsc1 if x > 0)}


def main():
    sms4 = load("sms_track2_v4.json")
    sms3 = load("sms_track2_v3.json")
    lrca4 = load("lrca_60cell_v4.json")
    lrca3 = load("lrca_60cell_v3.json")
    mp5 = load("rq2_cliffs_delta_v4_mp5.json")
    fried4 = load("rq3_friedman_v4.json")
    pc4 = load("rq4_pattern_coverage_v4.json")

    pools = {}
    for cell, v in sms4.items():
        put, mp = cell_key(cell)
        if mp == 1:
            pools[put] = v["inst"]

    out = {
        "_provenance": "scripts/audit_fix_numbers.py over frozen v3/v4 SSOT; primary map = pre-registered v3 (c-class MP5)",
        "h2_slice_v4_mp5primary": slice_stats(sms4),
        "h2_slice_v3_mp5primary": slice_stats(sms3),
        "h2_delta_ssot": {"v4_mp5": {"delta": mp5["cliffs_delta"], "ci": mp5["delta_ci_95"],
                                     "mean_aligned": mp5["mean_aligned"], "mean_cross": mp5["mean_cross"],
                                     "median_aligned": mp5["median_aligned"], "median_cross": mp5["median_cross"]},
                          "v3": mp5["comparison_v3"], "v4_mp1_posthoc": mp5["comparison_v4_mp1"]},
        "h1_v4": h1_counts(sms4),
        "h3_v4": per_class_delta(sms4),
        "h3_v3": per_class_delta(sms3),
        "class_means": {"v3": class_means(sms3), "v4": class_means(sms4)},
        "lrca_na_summary": {
            "v3": summarize_lrca(lrca3),
            "v4": summarize_lrca(lrca4),
        },
        "h4_v4": h4_readings(lrca4),
        "h4_v4_incl_l0": h4_incl_l0(sms4, lrca4),
        "gap_premise_support": gap_premise_support(sms4, PRIMARY),
        "v3_unresolved_census": v3_unresolved(sms3),
        "friedman_v4": {"chi2": round(fried4["chi2"], 2), "p": round(fried4["p_value"], 5),
                        "rank_means": fried4["rank_means_mp1_to_mp5"],
                        "per_class_raw_p": {c: round(fried4["per_class"][c]["p"], 4) for c in "abcd"},
                        "per_class_adj_p": {c: round(min(1.0, 4 * fried4["per_class"][c]["p"]), 4) for c in "abcd"},
                        "per_class_W": {c: round(fried4["per_class"][c]["chi2"] / 12, 3) for c in "abcd"}},
        "pattern_coverage_v4": {"mean": round(st.mean(v["pattern_coverage"] for v in pc4["per_put"].values()), 4),
                                "rho": round(pc4["spearman_rho"], 4), "tau": round(pc4["kendall_tau"], 4),
                                "per_put": pc4["per_put"]},
        "pool_sizes_v4": {"per_put": pools, "mean": round(st.mean(pools.values()), 1),
                          "min": min(pools.values()), "max": max(pools.values()),
                          "total": sum(pools.values())},
        "put_loc": loc_table(),
        "coverage_matrix_partition": coverage_partition(),
        "sms_totals_v4": {"total_kill_incidences_60cells": sum(v["killed"] for v in sms4.values()),
                          "cells_zero_sms": sum(1 for v in sms4.values() if v["sms"] == 0),
                          "mean_sms": round(st.mean(v["sms"] for v in sms4.values()), 4),
                          "median_sms": round(st.median(v["sms"] for v in sms4.values()), 4),
                          "std_sms": round(st.pstdev([v["sms"] for v in sms4.values()]), 4)},
    }
    xi = xi_audit(sms4)
    (RES / "xi_exactness_defect_v4.json").write_text(json.dumps(xi, indent=2) + "\n")
    out["xi_summary"] = {k: v for k, v in xi.items() if k != "per_cell"}
    (RES / "audit_fix_numbers.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2)[:6000])


if __name__ == "__main__":
    main()
