"""Diagnose why is_equivalent returns False for all 60 Track-2 cells.

Probes one (PUT, mutant, MR) triple at a time. Reports per-sample R(y_o, y_n)
verdicts, the |y_o - y_n| distribution, and whether the mutant ever produces
the SAME output as the original (which would indicate true equivalence).
"""
import sys
from dataclasses import dataclass
from typing import Callable, List

import numpy as np

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler


# Module-level dedupe set so we only print each new exception type once per
# process when probing many (PUT, mutant, MR) triples (LRCA reuse).
_SEEN_EXCEPTION_TYPES: set = set()


@dataclass
class EquivProbeResult:
    cell_id: str
    mutant_name: str
    n_samples: int
    n_R_pass: int           # samples where R-verdict on PUT == R-verdict on mutant
    n_R_fail: int           # samples where the two verdicts disagreed
    n_y_identical: int      # samples where mutant's y_new == PUT's y_new exactly
    n_exception: int        # samples where the inner mutant/PUT/MR call raised
                            # one of (ValueError, ArithmeticError, TypeError,
                            # RuntimeError). KeyboardInterrupt/SystemExit are
                            # NOT counted (they propagate).
    diff_min: float         # NaN when every sample raised (no diffs collected)
    diff_max: float         # NaN when every sample raised (no diffs collected)
    diff_mean: float        # NaN when every sample raised (no diffs collected)
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

    Convention: when every sample raises (n_exception == n_samples and diffs is
    empty), diff_min/diff_max/diff_mean are returned as float('nan'). This
    distinguishes "no observable behaviour" from "perfectly equivalent
    behaviour" (the previous sentinel of 0.0 was misleading).
    """
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=seed)
    xs = sampler.sample(n_samples)
    n_pass = n_fail = n_identical = n_exception = 0
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
        except (ValueError, ArithmeticError, TypeError, RuntimeError) as e:
            n_exception += 1
            _record_new_exception_type(e)
            continue
        try:
            r_pass_orig = mr.R(y_o_orig, y_n_orig)
            r_pass_mut = mr.R(y_o_mut, y_n_mut)
        except (ValueError, ArithmeticError, TypeError, RuntimeError) as e:
            n_exception += 1
            _record_new_exception_type(e)
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
        except (ValueError, ArithmeticError, TypeError, RuntimeError) as e:
            n_exception += 1
            _record_new_exception_type(e)
    if diffs:
        diffs_arr = np.array(diffs)
        diff_min = float(diffs_arr.min())
        diff_max = float(diffs_arr.max())
        diff_mean = float(diffs_arr.mean())
    else:
        # No samples produced a usable |y_n_mut - y_n_orig|: emit NaN so that
        # downstream consumers cannot mistake "all-raised" for "all-equal".
        nan = float("nan")
        diff_min = diff_max = diff_mean = nan
    return EquivProbeResult(
        cell_id=cell_id,
        mutant_name=mutant_name,
        n_samples=n_samples,
        n_R_pass=n_pass,
        n_R_fail=n_fail,
        n_y_identical=n_identical,
        n_exception=n_exception,
        diff_min=diff_min,
        diff_max=diff_max,
        diff_mean=diff_mean,
        epsilon_eq=epsilon_eq,
    )


def _record_new_exception_type(e: BaseException) -> None:
    """Print to stderr the FIRST time we see a given exception type.

    Helps surface unexpected failure modes during LRCA reuse without spamming
    logs (one line per type per process). The dedupe set is module-level.
    """
    t = type(e)
    if t not in _SEEN_EXCEPTION_TYPES:
        _SEEN_EXCEPTION_TYPES.add(t)
        print(
            f"[diagnosis] first {t.__name__}: {str(e)[:200]}",
            file=sys.stderr,
        )
