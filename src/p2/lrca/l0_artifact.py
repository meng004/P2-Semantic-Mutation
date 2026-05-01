"""LRCA Layer 0: artifact pre-screen.

A mutant is an "artifact" (not a legit semantic mutation) if it:
  - returns NaN on any sample
  - returns Inf on any sample
  - returns a constant (variance < 1e-12 over inputs)
  - is identical to the original on all samples (within 1e-9)

Otherwise it's LEGIT and the SMS denominator counts it.

Exception handling note: we narrow the catch to
``(ValueError, ArithmeticError, TypeError, RuntimeError)`` to match the
project pattern (see ``p2/avp/repeat.py``). The ``EXEC_ERROR`` label
exists specifically to capture mutant exceptions; narrowing avoids
silently swallowing ``BaseException`` subclasses such as
``KeyboardInterrupt`` / ``SystemExit``.
"""
from enum import Enum
from typing import Callable, Optional
import math
import numpy as np


_MUTANT_EXC = (ValueError, ArithmeticError, TypeError, RuntimeError)


class L0Label(str, Enum):
    LEGIT = "legit"
    NAN_OUTPUT = "nan_output"
    INF_OUTPUT = "inf_output"
    CONSTANT_OUTPUT = "constant_output"
    IDENTICAL_TO_ORIG = "identical_to_orig"
    EXEC_ERROR = "exec_error"


def classify_l0(mutant: Callable, n_samples: int = 30,
                original: Optional[Callable] = None,
                seed: int = 42) -> L0Label:
    """Classify a mutant against the L0 artifact pre-screen.

    Draws ``n_samples`` uniform samples from [0, 1] (seeded), evaluates
    the mutant on each, and returns the first matching artifact label
    in priority order: EXEC_ERROR -> NAN_OUTPUT -> INF_OUTPUT ->
    CONSTANT_OUTPUT -> IDENTICAL_TO_ORIG -> LEGIT.

    Parameters
    ----------
    mutant: callable accepting a single float, returning a float.
    n_samples: number of probe samples (default 30).
    original: optional reference callable; when provided, IDENTICAL_TO_ORIG
              fires if max |mutant(x) - original(x)| < 1e-9 over all probes.
    seed: RNG seed for reproducibility.
    """
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0.0, 1.0, n_samples)
    outs = []
    for x in xs:
        try:
            y = mutant(float(x))
            outs.append(float(y))
        except _MUTANT_EXC:
            return L0Label.EXEC_ERROR
    if any(math.isnan(o) for o in outs):
        return L0Label.NAN_OUTPUT
    if any(math.isinf(o) for o in outs):
        return L0Label.INF_OUTPUT
    if float(np.var(outs)) < 1e-12:
        return L0Label.CONSTANT_OUTPUT
    if original is not None:
        orig_outs = []
        for x in xs:
            try:
                orig_outs.append(float(original(float(x))))
            except _MUTANT_EXC:
                orig_outs.append(float("nan"))
        diffs = np.abs(np.array(outs) - np.array(orig_outs))
        if np.nanmax(diffs) < 1e-9:
            return L0Label.IDENTICAL_TO_ORIG
    return L0Label.LEGIT
