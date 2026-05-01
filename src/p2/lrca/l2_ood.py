"""LRCA L2 — Out-of-distribution failure (C3).

A killed mutant is C3 if its R-fail concentrates on input samples outside
the PUT's "trained" / "designed" input region. For our scalar PUTs all on
[0,1], we proxy OOD as inputs near the boundary (x < 0.05 or x > 0.95).

This module also retains the legacy ``is_ood_induced`` predicate used by
Round 7's decision-tree classifier (kept for backwards compatibility with
``tests/lrca/test_l2_ood.py``); the Round 8 dispatcher uses
``ood_fail_share`` instead.
"""
from typing import Callable, Sequence

import numpy as np

from p2.avp.interface import MR


def ood_fail_share(
    mutant: Callable, original: Callable, mr: MR,
    n_samples: int = 100, ood_band: float = 0.05, seed: int = 42,
) -> float:
    """Fraction of R-fails that occur on OOD inputs (boundary band).

    Draws ``n_samples`` uniform samples from [0, 1] (seeded for
    reproducibility, default seed=42) and counts how many R-failures
    fall into the boundary band ``[0, ood_band) ∪ (1 - ood_band, 1]``.
    Returns 0.0 when there are no R-failures at all.

    Exceptions during ``mr.r``, ``mutant``, or ``mr.R`` are narrowed to
    ``(ValueError, ArithmeticError, TypeError, RuntimeError)`` per the
    project pattern; offending samples are skipped and don't contribute
    to either numerator or denominator.

    The ``original`` parameter is unused by this proxy (boundary band is
    purely input-side); it's kept in the signature so the dispatcher can
    pass it uniformly alongside the L0 / L3 helpers.
    """
    del original  # unused; reserved for future original-vs-mutant proxies
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0.0, 1.0, n_samples)
    fails_total = 0
    fails_ood = 0
    for x in xs:
        try:
            xr = mr.r(float(x))
            y_o = mutant(float(x))
            y_n = mutant(float(xr))
            r_pass = mr.R(y_o, y_n)
        except (ValueError, ArithmeticError, TypeError, RuntimeError):
            continue
        if not r_pass:
            fails_total += 1
            if x < ood_band or x > 1.0 - ood_band:
                fails_ood += 1
    return fails_ood / fails_total if fails_total else 0.0


def is_ood_induced(
    fails_per_input: Sequence[bool], valid_mask: Sequence[bool],
) -> bool:
    """Legacy Round 7 predicate: True iff failures occur only on inputs
    outside the PUT's valid domain.

    Retained for backwards compatibility with the legacy decision-tree
    classifier (``p2.lrca.decision_tree``). The Round 8 dispatcher
    supersedes this with ``ood_fail_share`` which returns a continuous
    fraction rather than a binary verdict.
    """
    fails_inside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and v)
    fails_outside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and not v)
    return fails_inside == 0 and fails_outside > 0
