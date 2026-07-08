"""A5 mutant."""
import numpy as np
from scipy.interpolate import CubicSpline

def _build():
    ti = np.linspace(0.0, 1.0, 5)
    return CubicSpline(ti, np.sin(np.pi * ti), bc_type="natural")


_SPLINE = _build()


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))