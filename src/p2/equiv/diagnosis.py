"""Diagnose why is_equivalent returns False for all 60 Track-2 cells.

Probes one (PUT, mutant, MR) triple at a time. Reports per-sample R(y_o, y_n)
verdicts, the |y_o - y_n| distribution, and whether the mutant ever produces
the SAME output as the original (which would indicate true equivalence).
"""
from dataclasses import dataclass
from typing import Callable, List

import numpy as np

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler


@dataclass
class EquivProbeResult:
    cell_id: str
    mutant_name: str
    n_samples: int
    n_R_pass: int           # samples where R-verdict on PUT == R-verdict on mutant
    n_R_fail: int           # samples where the two verdicts disagreed
    n_y_identical: int      # samples where mutant's y_new == PUT's y_new exactly
    diff_min: float
    diff_max: float
    diff_mean: float
    epsilon_eq: float


def probe_equivalence(
    put: Callable,
    mutant: Callable,
    mr: MR,
    cell_id: str,
    mutant_name: str,
    n_samples: int = 1000,
    epsilon_eq: float = 1e-6,
    seed: int = 42,
) -> EquivProbeResult:
    """Sample n_samples inputs, compute y_orig vs y_new, report distribution.

    Note: the project's UniformSampler.sample(k_eq) returns a (k_eq, dim) array,
    so we draw all samples up-front and iterate. This preserves seeded
    reproducibility while letting each iteration see a distinct x.
    """
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=seed)
    xs = sampler.sample(n_samples)
    n_pass = n_fail = n_identical = 0
    diffs: List[float] = []
    for i in range(n_samples):
        raw = xs[i]
        if isinstance(raw, np.ndarray):
            x = float(raw.flat[0])
        else:
            x = float(raw)
        try:
            x_r = mr.r(x)
            y_o_orig = put(x)
            y_n_orig = put(x_r)
            y_o_mut = mutant(x)
            y_n_mut = mutant(x_r)
        except Exception:
            continue
        try:
            r_pass_orig = mr.R(y_o_orig, y_n_orig)
            r_pass_mut = mr.R(y_o_mut, y_n_mut)
        except Exception:
            continue
        if r_pass_orig == r_pass_mut:
            n_pass += 1
        else:
            n_fail += 1
        try:
            d = abs(float(y_n_mut) - float(y_n_orig))
            diffs.append(d)
            if d < 1e-15:
                n_identical += 1
        except Exception:
            pass
    diffs_arr = np.array(diffs) if diffs else np.array([0.0])
    return EquivProbeResult(
        cell_id=cell_id,
        mutant_name=mutant_name,
        n_samples=n_samples,
        n_R_pass=n_pass,
        n_R_fail=n_fail,
        n_y_identical=n_identical,
        diff_min=float(diffs_arr.min()),
        diff_max=float(diffs_arr.max()),
        diff_mean=float(diffs_arr.mean()),
        epsilon_eq=epsilon_eq,
    )
