"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.sin(np.pi * _TI)
_SPLINE = CubicSpline(_TI, _YI, axis=0, bc_type="clamped")


def program(x) -> float:
    return float(_SPLINE(float(x)))