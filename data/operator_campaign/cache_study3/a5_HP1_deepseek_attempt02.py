import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_Y = np.sin(np.pi * _TI)
_SPLINE = CubicSpline(_TI, _Y, bc_type=((1, 0.0), (1, 0.0)))

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))