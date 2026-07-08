"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_KNOTS = [i / 4.0 for i in range(5)]
_TI = np.asarray(_KNOTS, dtype=float)
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))