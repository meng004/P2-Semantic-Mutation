"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.array([np.cos(np.pi * t) for t in _TI])
_SPLINE = CubicSpline(_TI, _YI, bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))