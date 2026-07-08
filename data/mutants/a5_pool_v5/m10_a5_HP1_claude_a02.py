"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_BC = "clamped"
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type=_BC)


def program(x) -> float:
    return float(_SPLINE(float(x)))