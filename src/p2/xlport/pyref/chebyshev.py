"""Python-side reference for XL program 'chebyshev' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import numpy as np
from numpy.polynomial import chebyshev as _C

_COEF = _C.chebinterpolate(np.exp, 12)


def program(x) -> float:
    return float(_C.chebval(2.0 * float(x) - 1.0, _COEF))
