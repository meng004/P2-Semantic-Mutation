"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.cos(np.pi * _TI)


def program(x) -> float:
    spline = CubicSpline(_TI, _YI, bc_type="natural")
    return float(spline(float(x)))