"""Friedman test for RQ3 cross-class comparison.

Block: PUT (12 levels: a1..d3)
Treatment: MP (5 levels: MP1..MP5)
Value: SMS

Friedman χ² tests whether MP-effect is consistent across PUTs.
Complements §5.8.2 sign test by providing a formal non-parametric p-value.

Reads data/results/sms_track2_v3.json by default; pass --v2 to read v2.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import friedmanchisquare

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2", action="store_true", help="use sms_track2_v2.json")
    args = parser.parse_args()
    sms_file = "sms_track2_v2.json" if args.v2 else "sms_track2_v3.json"
    sms = json.loads((ROOT / "data/results" / sms_file).read_text())

    puts = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3", "d1", "d2", "d3"]
    M = np.zeros((len(puts), 5))
    for i, p in enumerate(puts):
        for j, mp in enumerate([1, 2, 3, 4, 5]):
            cell = f"{p.upper()}_MP{mp}"
            M[i, j] = sms.get(cell, {}).get("sms", 0.0)

    try:
        res = friedmanchisquare(*[M[:, j] for j in range(5)])
        stat = float(res.statistic)
        p_main = float(res.pvalue)
    except ValueError as exc:
        stat, p_main = float("nan"), 1.0
        print(f"WARN main Friedman: {exc}")

    ranks = np.argsort(np.argsort(M, axis=1), axis=1) + 1
    rank_means = ranks.mean(axis=0).tolist()

    per_class = {}
    for cls in "abcd":
        cls_puts = [p for p in puts if p[0] == cls]
        Mc = np.zeros((len(cls_puts), 5))
        for i, p in enumerate(cls_puts):
            for j, mp in enumerate([1, 2, 3, 4, 5]):
                cell = f"{p.upper()}_MP{mp}"
                Mc[i, j] = sms.get(cell, {}).get("sms", 0.0)
        if Mc.shape[0] >= 2:
            try:
                cres = friedmanchisquare(*[Mc[:, j] for j in range(5)])
                cs = float(cres.statistic)
                cp = float(cres.pvalue)
            except ValueError:
                cs, cp = float("nan"), 1.0
            per_class[cls] = {"chi2": cs, "p": cp, "n_puts": Mc.shape[0]}
        else:
            per_class[cls] = {"n_puts": Mc.shape[0], "skipped": "n < 2"}

    out = {
        "source": sms_file,
        "design": "PUT (block, n=12) × MP (treatment, k=5)",
        "chi2": stat if not np.isnan(stat) else None,
        "p_value": p_main,
        "df": 4,
        "rank_means_mp1_to_mp5": [round(r, 3) for r in rank_means],
        "per_class": per_class,
        "interpretation": (
            "p < 0.05 ⇒ MP-effect varies across PUTs (cross-class consistency rejected)"
            if p_main < 0.05 else
            "p ≥ 0.05 ⇒ no significant MP × PUT effect; consistent with §5.8.2 sign test direction"
        ),
    }
    out_path = ROOT / "data/results/rq3_friedman.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nsaved -> {out_path}")


if __name__ == "__main__":
    main()
