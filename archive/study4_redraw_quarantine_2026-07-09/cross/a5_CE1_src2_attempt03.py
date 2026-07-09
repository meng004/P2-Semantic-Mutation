"""A5: Cubic-spline interpolation — piecewise-polynomial reconstruction (scalar x∈[0,1] interface).

Library: scipy.interpolate.CubicSpline (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html

program(x) where x ∈ [0,1] scalar (evaluation point).
Natural cubic spline through 17 samples of f(t)=sin(π t) on [0,1], evaluated at t=x.
Target is symmetric about ½: sin(π(1-t))=sin(π t) → S(x)=S(1-x).
"""
import numpy as np
from scipy.interpolate import CubicSpline


def program(x) -> float:
    x = float(x)
    # Mutated: Changed the sample grid size from 17 to 5 (coarse grid)
    knots = np.linspace(0.0, 1.0, 5)
    values = np.sin(np.pi * knots)
    spline_evaluator = CubicSpline(knots, values, bc_type="natural")
    return float(spline_evaluator(x))