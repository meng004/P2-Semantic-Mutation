"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))