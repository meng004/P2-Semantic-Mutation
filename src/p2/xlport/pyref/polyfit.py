"""Python-side reference for XL program 'polyfit' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np

_T = np.arange(33) / 32.0


def program(x) -> float:
    d = np.exp((0.5 + float(x)) * _T)
    coef = np.polyfit(_T, d, 3)
    return float(np.polyval(coef, 0.6))
