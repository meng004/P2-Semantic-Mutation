import numpy as np
from scipy.interpolate import CubicSpline

_GRID = np.linspace(0.0, 1.0, num=17)
_VALUES = np.sin(np.pi * _GRID)

def _make_spline():
    return CubicSpline(_GRID, _VALUES, bc_type="clamped")

_SPLINE = _make_spline()

def program(x) -> float:
    return float(_SPLINE(float(x)))