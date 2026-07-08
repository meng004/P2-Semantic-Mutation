"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 5, endpoint=True)
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")


def program(x) -> float:
    return float(_SPLINE(float(x)))