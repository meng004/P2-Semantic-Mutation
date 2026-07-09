import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_ARG = np.pi * _TI
_SPLINE = CubicSpline(_TI, np.sin(_ARG), bc_type="clamped")

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))