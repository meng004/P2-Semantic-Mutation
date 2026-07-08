"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

def _spline():
    ti = np.linspace(0.0, 1.0, 17)
    return CubicSpline(ti, np.sin(np.pi * ti), bc_type="clamped")


_SPLINE = _spline()


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))