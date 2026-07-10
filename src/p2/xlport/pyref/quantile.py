"""Python-side reference for XL program 'quantile' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

import numpy as np

_V = np.array([-3.7, -2.9, -2.3, -1.7, -1.3, -0.9, -0.6, -0.35, -0.2, -0.08, 0.0, 0.08, 0.2, 0.35, 0.6, 0.9, 1.3, 1.7, 2.3, 2.9, 3.7])


def program(x) -> float:
    return float(np.quantile(_V, float(x)))
