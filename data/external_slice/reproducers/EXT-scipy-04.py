#!/usr/bin/env python3
"""Dual-arm trigger for EXT-scipy-04 (scipy issue #11186).

Same seed, input grid, and property check for buggy and fixed arms.
Issue-described behaviour: for negative skew, pearson3 CDF on an increasing
grid must be monotone non-decreasing and lie in [0, 1].
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np
    import scipy
    from scipy.stats import pearson3

    rng = np.random.RandomState(seed)
    # Keep the issue grid fixed; seed only reserved for future draws.
    _ = rng.randint(0, 2**31 - 1)
    skew = -0.5
    xs = np.linspace(-2.0, 1.5, 5)
    cdf = np.asarray(pearson3.cdf(xs, skew), dtype=float)
    sf = np.asarray(pearson3.sf(xs, skew), dtype=float)
    xd = np.linspace(-4.0, 4.0, 201)
    cdf_dense = np.asarray(pearson3.cdf(xd, skew), dtype=float)

    mono_grid = bool(np.all(np.diff(cdf) >= -1e-15))
    mono_dense = bool(np.all(np.diff(cdf_dense) >= -1e-15))
    in_01 = bool(np.all((cdf_dense >= 0.0) & (cdf_dense <= 1.0)))
    sf_nonincreasing = bool(np.all(np.diff(sf) <= 1e-15))
    property_holds = mono_grid and mono_dense and in_01 and sf_nonincreasing

    return {
        "neutral_id": "EXT-scipy-04",
        "seed": seed,
        "input": {
            "skew": skew,
            "x_issue_grid": xs.tolist(),
            "x_dense_grid_spec": {"start": -4.0, "stop": 4.0, "num": 201},
        },
        "observed_output": {
            "cdf_issue_grid": cdf.tolist(),
            "sf_issue_grid": sf.tolist(),
            "cdf_monotone_issue_grid": mono_grid,
            "cdf_monotone_dense_grid": mono_dense,
            "cdf_in_unit_interval": in_01,
            "sf_nonincreasing_issue_grid": sf_nonincreasing,
        },
        "expected_property": (
            "For skew=-0.5, pearson3 CDF on a strictly increasing grid is "
            "monotone non-decreasing and in [0,1]; SF is monotone non-increasing."
        ),
        "property_holds": property_holds,
        "package_version": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "scipy": scipy.__version__,
            "numpy": np.__version__,
        },
        "exit_status": 0 if property_holds else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    payload = evaluate(args.seed)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"], "package_version": payload["package_version"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
