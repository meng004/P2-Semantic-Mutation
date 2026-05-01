"""Aggregate all numbers cited in 论文初稿P2.md §5.6-5.9 into a single JSON.

Set env SMS_VERSION=v3 (default) to read sms_track2_v3 + lrca_60cell_v3 +
rq2/3/4_*_v3.json and write paper_numbers_v3.json. Set SMS_VERSION=v2 for
the legacy (Round 4) files.
"""
import json
import math
import os
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "data/results"
import sys as _sys
_sys.path.insert(0, str(ROOT / "src"))
from p2.config.primary import PRIMARY_CELLS as PRIMARY  # type: ignore[import-not-found]  # noqa: E402

VERSION = os.environ.get("SMS_VERSION", "v3")
_suffix = f"_{VERSION}" if VERSION != "v2" else ""
SMS_FILE = f"sms_track2{_suffix}.json" if VERSION != "v2" else "sms_track2_v2.json"
LRCA_FILE = f"lrca_60cell{_suffix}.json" if VERSION != "v2" else "lrca_60cell.json"
RQ2_FILE = f"rq2_cliffs_delta{_suffix}.json" if VERSION != "v2" else "rq2_cliffs_delta.json"
RQ3_FILE = f"rq3_mixed_effects{_suffix}.json" if VERSION != "v2" else "rq3_mixed_effects.json"
RQ4_FILE = f"rq4_pattern_coverage{_suffix}.json" if VERSION != "v2" else "rq4_pattern_coverage.json"
OUT_FILE = f"paper_numbers{_suffix}.json" if VERSION != "v2" else "paper_numbers.json"
print(f"build_paper_numbers: VERSION={VERSION} writing {OUT_FILE}")


def _load(name):
    return json.loads((RESULTS / name).read_text())


def _is_inf(v):
    if isinstance(v, float):
        return math.isinf(v)
    if isinstance(v, str):
        return v in ("Infinity", "inf", "+inf")
    return False


def main() -> None:
    sms = _load(SMS_FILE)
    lrca = _load(LRCA_FILE)
    rq2 = _load(RQ2_FILE)
    rq3 = _load(RQ3_FILE)
    rq4 = _load(RQ4_FILE)
    try:
        friedman = _load("rq3_friedman.json")
    except FileNotFoundError:
        friedman = None

    aligned, cross = [], []
    per_class_aligned = {"a": [], "b": [], "c": [], "d": []}
    per_class_cross = {"a": [], "b": [], "c": [], "d": []}
    for cell, v in sms.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        s = v["sms"]
        if mp_k == PRIMARY[put_id]:
            aligned.append(s)
            per_class_aligned[put_id[0]].append(s)
        else:
            cross.append(s)
            per_class_cross[put_id[0]].append(s)

    all_sms = [v["sms"] for v in sms.values()]
    c1_shares = [r["c1_share"] for r in lrca.values()]
    suspects = [r["suspect_share"] for r in lrca.values()]

    h5_threshold = 0.20  # paper §5.2 H5
    h5_cells_pass = sum(1 for s in suspects if s <= h5_threshold)

    sign_passes = 0
    for c in "abcd":
        m_a = float(np.mean(per_class_aligned[c])) if per_class_aligned[c] else 0.0
        m_c = float(np.mean(per_class_cross[c])) if per_class_cross[c] else 0.0
        if m_a > m_c:
            sign_passes += 1

    odds = rq2.get("odds_ratio_median", 0.0)
    out = {
        "rq1": {
            "n_cells": len(sms),
            "mean_sms": round(float(np.mean(all_sms)), 4),
            "median_sms": round(float(np.median(all_sms)), 4),
            "std_sms": round(float(np.std(all_sms, ddof=1)), 4),
            "n_zero_sms": int(sum(1 for s in all_sms if s == 0.0)),
            "mean_c1_share": round(float(np.mean(c1_shares)), 4),
            "mean_suspect_share": round(float(np.mean(suspects)), 4),
            "h5_threshold_suspect": h5_threshold,
            "h5_cells_pass": h5_cells_pass,
            "h5_pass_ratio": round(h5_cells_pass / len(sms), 4),
        },
        "rq2": {
            "n_aligned": len(aligned),
            "n_cross": len(cross),
            "mean_aligned": round(float(np.mean(aligned)), 4),
            "mean_cross": round(float(np.mean(cross)), 4),
            "median_aligned": round(float(np.median(aligned)), 4),
            "median_cross": round(float(np.median(cross)), 4),
            "cliffs_delta": round(rq2["cliffs_delta"], 4),
            "delta_ci_95_lo": round(rq2["delta_ci_95"][0], 4),
            "delta_ci_95_hi": round(rq2["delta_ci_95"][1], 4),
            "h2_threshold_delta": rq2["h2_threshold_delta"],
            "h2_delta_pass": rq2["h2_delta_pass"],
            "h2_threshold_ratio": rq2["h2_threshold_ratio"],
            "h2_ratio_pass": rq2["h2_ratio_pass"],
            "odds_ratio_inf": _is_inf(odds),
        },
        "rq3": {
            "n_observations": rq3["n_observations"],
            "class_mean_a": round(rq3["class_means"]["a"], 4),
            "class_mean_b": round(rq3["class_means"]["b"], 4),
            "class_mean_c": round(rq3["class_means"]["c"], 4),
            "class_mean_d": round(rq3["class_means"]["d"], 4),
            "class_max": max(rq3["class_means"], key=rq3["class_means"].get),
            "class_min": min(rq3["class_means"], key=rq3["class_means"].get),
            "primary_converged": rq3["converged"],
            "fit_error": rq3.get("fit_error", ""),
            "fallback_model": rq3.get("fallback_model", ""),
            "fallback_note": rq3.get("fallback_note", ""),
            "fallback_p_class_b": round(
                rq3.get("fallback_p_values", {}).get("C(class)[T.b]", float("nan")), 4),
            "fallback_p_class_c": round(
                rq3.get("fallback_p_values", {}).get("C(class)[T.c]", float("nan")), 4),
            "fallback_p_class_d": round(
                rq3.get("fallback_p_values", {}).get("C(class)[T.d]", float("nan")), 4),
            "sign_test_aligned_above_cross": sign_passes,
            "friedman_chi2": round(friedman["chi2"], 4) if friedman else None,
            "friedman_p": round(friedman["p_value"], 4) if friedman else None,
            "friedman_per_class_p": (
                {c: round(friedman["per_class"][c]["p"], 4)
                 for c in "abcd" if "p" in friedman["per_class"].get(c, {})}
                if friedman else {}
            ),
        },
        "rq4": {
            "spearman_rho": round(rq4["spearman_rho"], 4),
            "spearman_p": round(rq4["spearman_p"], 4),
            "kendall_tau": round(rq4["kendall_tau"], 4),
            "kendall_p": round(rq4["kendall_p"], 4),
            "n_puts": rq4["n"],
            "min_pc": round(min(v["pattern_coverage"] for v in rq4["per_put"].values()), 4),
            "max_pc": round(max(v["pattern_coverage"] for v in rq4["per_put"].values()), 4),
            "mean_pc": round(float(np.mean(
                [v["pattern_coverage"] for v in rq4["per_put"].values()])), 4),
        },
    }

    out_path = RESULTS / OUT_FILE
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"saved -> {out_path}")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
