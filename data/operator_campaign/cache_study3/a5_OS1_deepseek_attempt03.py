import numpy as np
from scipy.interpolate import CubicSpline

_PI = np.pi
_TI = np.linspace(0.0, 1.0, 17)
_SPLINE = CubicSpline(_TI, np.cos(_PI * _TI), bc_type="natural")

def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))