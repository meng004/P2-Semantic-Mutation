"""RQ4: per-PUT pattern coverage vs mean SMS over 5 MPs.

Pattern coverage = fraction of (MP_k, R_outcome) cells exercised by running
each mutant's program on a 10-point grid through each MP's r/R pair.

Output: data/results/rq4_pattern_coverage.json
"""
import importlib.util
import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS as PRIMARY  # type: ignore[import-not-found]  # noqa: E402
from p2.stats.pattern_coverage import compute_pattern_coverage  # noqa: E402

VERSION = os.environ.get("SMS_VERSION", "v3")
SMS_FILE = "sms_track2_v3.json" if VERSION == "v3" else "sms_track2_v2.json"
OUT_FILE = "rq4_pattern_coverage_v3.json" if VERSION == "v3" else "rq4_pattern_coverage.json"
print(f"compute_rq4: SMS_VERSION={VERSION} reading {SMS_FILE} writing {OUT_FILE}")

NARROW_EXC = (ValueError, ArithmeticError, TypeError, RuntimeError,
              ImportError, OSError, AttributeError)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> None:
    sms = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

    per_put = {}
    for put_id in PRIMARY:
        pool_v3 = ROOT / f"data/mutants/{put_id}_pool_v3"
        pool_v2 = ROOT / f"data/mutants/{put_id}_pool"
        if VERSION == "v3" and pool_v3.exists():
            pool_dir = pool_v3
        elif pool_v2.exists():
            pool_dir = pool_v2
        else:
            pool_dir = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm"
        mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
        outcomes = []
        xs = np.linspace(0.05, 0.95, 10)
        for fp in sorted(pool_dir.glob("m*.py")):
            try:
                mut_mod = _load(f"_m_{put_id}_{fp.stem}", fp)
            except NARROW_EXC:
                continue
            for mp_k in (1, 2, 3, 4, 5):
                r = getattr(mrs_mod, f"r_mp{mp_k}")
                R = getattr(mrs_mod, f"R_mp{mp_k}")
                for x in xs:
                    try:
                        y_o = mut_mod.program(float(x))
                        y_n = mut_mod.program(float(r(x)))
                        outcomes.append((mp_k, bool(R(y_o, y_n))))
                    except NARROW_EXC:
                        continue
        cov = compute_pattern_coverage(outcomes, n_mps=5)
        cell_smses = [v["sms"] for k, v in sms.items()
                      if k.startswith(put_id.upper() + "_")]
        if not cell_smses:
            raise KeyError(f"no SMS cells found for PUT {put_id}")
        per_put[put_id] = {
            "pattern_coverage": round(cov, 4),
            "mean_sms_over_5_cells": round(float(np.mean(cell_smses)), 4),
        }

    cov_arr = [v["pattern_coverage"] for v in per_put.values()]
    sms_arr = [v["mean_sms_over_5_cells"] for v in per_put.values()]
    sp = spearmanr(cov_arr, sms_arr)
    kt = kendalltau(cov_arr, sms_arr)
    report = {
        "per_put": per_put,
        "spearman_rho": float(sp.statistic),  # type: ignore[union-attr]
        "spearman_p": float(sp.pvalue),  # type: ignore[union-attr]
        "kendall_tau": float(kt.statistic),  # type: ignore[union-attr]
        "kendall_p": float(kt.pvalue),  # type: ignore[union-attr]
        "n": len(per_put),
    }
    out = ROOT / "data/results" / OUT_FILE
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
