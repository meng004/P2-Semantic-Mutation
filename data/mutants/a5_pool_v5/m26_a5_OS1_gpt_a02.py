"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_ANGLES = np.pi * _TI
_SPLINE = CubicSpline(_TI, np.cos(_ANGLES), bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))