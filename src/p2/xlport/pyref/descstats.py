"""Python-side reference for XL program 'descstats' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np

_PHI = 1.6180339887498949
_I = np.arange(1, 257, dtype=float)
_U = _I * _PHI - np.floor(_I * _PHI)


def program(x) -> float:
    w = 0.4 * 2.0 ** (2.0 * float(x) - 1.0)
    s = 0.5 + (_U - 0.5) * w
    return float(np.std(s, ddof=1))
