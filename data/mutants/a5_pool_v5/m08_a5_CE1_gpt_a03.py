"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_SAMPLES = 5
_TI = np.linspace(0.0, 1.0, _SAMPLES)
_YI = np.sin(np.pi * _TI)
_SPLINE = CubicSpline(_TI, _YI, bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))