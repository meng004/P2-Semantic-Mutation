"""Python-side reference for XL program 'hermite' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np
from scipy.interpolate import CubicHermiteSpline

_T = np.arange(17) / 16.0
_H = CubicHermiteSpline(_T, np.exp(_T), np.exp(_T))


def program(x) -> float:
    return float(_H(float(x)))
