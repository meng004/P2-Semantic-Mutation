import numpy as np
from scipy.interpolate import CubicSpline

_N = 5
_TI = np.linspace(0.0, 1.0, _N)
_SPLINE = CubicSpline(_TI, np.sin(np.pi * _TI), bc_type="natural")

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))