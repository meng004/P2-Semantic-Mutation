import numpy as np
from scipy.interpolate import CubicSpline

_GRID = np.linspace(0.0, 1.0, 17)
_VALUES = np.sin(np.pi * _GRID)
_SPLINE = CubicSpline(_GRID, _VALUES, bc_type="clamped")


def program(x) -> float:
    return float(_SPLINE(float(x)))