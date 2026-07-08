"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)


def _target(t):
    return np.cos(np.pi * t)


_SPLINE = CubicSpline(_TI, _target(_TI), bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))