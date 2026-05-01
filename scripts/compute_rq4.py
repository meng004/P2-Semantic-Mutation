"""RQ4: per-PUT pattern coverage vs mean SMS over 5 MPs.

Pattern coverage = fraction of (MP_k, R_outcome) cells exercised by running
each mutant's program on a 10-point grid through each MP's r/R pair.

Output: data/results/rq4_pattern_coverage.json
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.stats.pattern_coverage import compute_pattern_coverage  # noqa: E402

PRIMARY = {"a1": 1, "a2": 1, "a3": 1,
           "b1": 2, "b2": 2, "b3": 2,
           "c1": 5, "c2": 5, "c3": 5,
           "d1": 2, "d2": 2, "d3": 2}

NARROW_EXC = (ValueError, ArithmeticError, TypeError, RuntimeError,
              ImportError, OSError, AttributeError)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    sms = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())

    per_put = {}
    for put_id in PRIMARY:
        pool_dir = ROOT / f"data/mutants/{put_id}_pool"
        if not pool_dir.exists():
            pool_dir = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm"
        mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
        outcomes = []
        for fp in sorted(pool_dir.glob("m*.py")):
            try:
                mut_mod = _load(f"_m_{put_id}_{fp.stem}", fp)
            except NARROW_EXC:
                continue
            for mp_k in (1, 2, 3, 4, 5):
                r = getattr(mrs_mod, f"r_mp{mp_k}")
                R = getattr(mrs_mod, f"R_mp{mp_k}")
                try:
                    xs = np.linspace(0.05, 0.95, 10)
                    for x in xs:
                        y_o = mut_mod.program(float(x))
                        y_n = mut_mod.program(float(r(x)))
                        outcomes.append((mp_k, bool(R(y_o, y_n))))
                except NARROW_EXC:
                    pass
        cov = compute_pattern_coverage(outcomes, n_mps=5)
        cell_smses = [v["sms"] for k, v in sms.items()
                      if k.startswith(put_id.upper() + "_")]
        per_put[put_id] = {
            "pattern_coverage": round(cov, 4),
            "mean_sms_over_5_cells": round(float(np.mean(cell_smses)), 4),
        }

    cov_arr = [v["pattern_coverage"] for v in per_put.values()]
    sms_arr = [v["mean_sms_over_5_cells"] for v in per_put.values()]
    rho, p_rho = spearmanr(cov_arr, sms_arr)
    tau, p_tau = kendalltau(cov_arr, sms_arr)
    report = {
        "per_put": per_put,
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "kendall_tau": float(tau),
        "kendall_p": float(p_tau),
        "n": len(per_put),
    }
    out = ROOT / "data/results/rq4_pattern_coverage.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
