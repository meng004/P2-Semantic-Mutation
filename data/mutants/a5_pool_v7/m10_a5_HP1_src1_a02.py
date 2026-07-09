import numpy as np
from scipy.interpolate import CubicSpline

def _make_spline():
    ti = np.linspace(0.0, 1.0, 17)
    yi = np.sin(np.pi * ti)
    return CubicSpline(ti, yi, bc_type="clamped")

_SPLINE = _make_spline()

def program(x) -> float:
    return float(_SPLINE(float(x)))