"""Python-side reference for XL program 'sinc' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

import numpy as np


def program(x) -> float:
    return float(np.sinc(4.0 * float(x) - 2.0))
