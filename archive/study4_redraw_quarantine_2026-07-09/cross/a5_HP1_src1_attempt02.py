"""A5: Cubic-spline interpolation — piecewise-polynomial reconstruction (scalar x∈[0,1] interface).

Library: scipy.interpolate.CubicSpline (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

program(x) where x ∈ [0,1] scalar (evaluation point).
Natural cubic spline through 17 samples of f(t)=sin(π t) on [0,1], evaluated at t=x.
Target is symmetric about ½: sin(π(1-t))=sin(π t) → S(x)=S(1-x).
"""
import numpy as np
from scipy.interpolate import CubicSpline

_TI = np.linspace(0.0, 1.0, 17)
_YI = np.sin(np.pi * _TI)
_SPLINE = CubicSpline(x=_TI, y=_YI, bc_type="clamped")


def program(x) -> float:
    x = float(x)
    y = _SPLINE(x)
    return float(y)