"""Python-side reference for XL program 'histstats' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference
(the documented gsl_histogram_mean binned-mean formula)."""

import numpy as np

_PHI = 1.6180339887498949
_I = np.arange(1, 513, dtype=float)
_U = _I * _PHI - np.floor(_I * _PHI)


def program(x) -> float:
    s = _U ** (1.0 + 2.0 * float(x))
    counts, edges = np.histogram(s, bins=32, range=(0.0, 1.0))
    mids = 0.5 * (edges[:-1] + edges[1:])
    return float((counts * mids).sum() / counts.sum())
