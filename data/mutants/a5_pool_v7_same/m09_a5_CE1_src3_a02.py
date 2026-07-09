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


def _build_spline(n):
    ti = np.linspace(0.0, 1.0, n)
    return CubicSpline(ti, np.sin(np.pi * ti), bc_type="natural")


_SPLINE = _build_spline(_N_KNOTS)


def program(x) -> float:
    x = float(x)
    return float(_SPLINE(x))