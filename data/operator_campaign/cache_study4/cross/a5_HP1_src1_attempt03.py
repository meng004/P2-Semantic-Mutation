import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.sin(np.pi * _TI)
_SPLINE_OPTIONS = {"bc_type": "clamped"}
_SPLINE = CubicSpline(_TI, _YI, **_SPLINE_OPTIONS)


def program(x) -> float:
    return float(_SPLINE(float(x)))