"""A5: Cubic-spline interpolation — piecewise-polynomial reconstruction (scalar x∈[0,1] interface).

Library: scipy.interpolate.CubicSpline (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

program(x) where x ∈ [0,1] scalar (evaluation point).
Natural cubic spline through 17 samples of f(t)=sin(π t) on [0,1], evaluated at t=x.
Target is symmetric about ½: sin(π(1-t))=sin(π t) → S(x)=S(1-x).
"""
import numpy as np
from scipy.interpolate import CubicSpline

_N_KNOTS = 17
_BC = "clamped"

_spline_cache = {}


def _get_spline():
    if _BC not in _spline_cache:
        ti = np.linspace(0.0, 1.0, _N_KNOTS)
        _spline_cache[_BC] = CubicSpline(ti, np.sin(np.pi * ti), bc_type=_BC)
    return _spline_cache[_BC]


def program(x) -> float:
    x = float(x)
    return float(_get_spline()(x))