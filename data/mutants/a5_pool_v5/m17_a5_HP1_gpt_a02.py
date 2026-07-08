"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.sin(np.pi * _TI)
_KWARGS = {"bc_type": "clamped"}
_SPLINE = CubicSpline(_TI, _YI, **_KWARGS)


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))