"""A5: Cubic-spline interpolation — piecewise-polynomial reconstruction (scalar x∈[0,1] interface).

Library: scipy.interpolate.CubicSpline (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

program(x) where x ∈ [0,1] scalar (evaluation point).
Natural cubic spline through samples of f(t)=sin(π t) on [0,1], evaluated at t=x.
Target is symmetric about ½: sin(π(1-t))=sin(π t) → S(x)=S(1-x).
"""
import numpy as np
from scipy.interpolate import CubicSpline

_N_KNOTS = 5
_SPLINE = None


def _build_spline():
    global _SPLINE
    if _SPLINE is None:
        ti = np.linspace(0.0, 1.0, _N_KNOTS)
        _SPLINE = CubicSpline(ti, np.sin(np.pi * ti), bc_type="natural")
    return _SPLINE


def program(x) -> float:
    x = float(x)
    spline = _build_spline()
    return float(spline(x))