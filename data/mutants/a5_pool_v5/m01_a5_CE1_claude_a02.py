"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_N_KNOTS = 5
_TI = np.linspace(0.0, 1.0, num=_N_KNOTS)
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")


def program(x) -> float:
    return float(_SPLINE(float(x)))