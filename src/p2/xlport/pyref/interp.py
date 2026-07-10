"""Python-side reference for XL program 'interp' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np
from scipy.interpolate import interp1d

_T = np.arange(17) / 16.0
_F = interp1d(_T, np.exp(_T), kind="linear")


def program(x) -> float:
    return float(_F(float(x)))
