import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.array([i / 4.0 for i in range(5)])
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))