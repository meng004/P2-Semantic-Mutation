import numpy as np
from scipy.interpolate import CubicSpline

_BC_TYPE = 'clamped'
_TI = np.linspace(0.0, 1.0, 17)
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type=_BC_TYPE)

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))