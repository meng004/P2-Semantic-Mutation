"""MR functions for B3 Monte Carlo Integration.

Primary MP: MP1 (Conservation/linearity).
  r_mp1(x) = min(x + 0.1, 0.9): shifts integrand constant by 0.1.
  R_mp1: |y_new - y_orig - 0.1| < 0.02 (linearity: ∫(x+0.1+t²)=∫(x+t²)+0.1).
Trivial: r_trivial, R_trivial for MP2/3/4/5.
"""
import numpy as np


def r_mp1(x) -> float:
    return float(min(float(x) + 0.1, 0.9))


def R_mp1(y_orig, y_new) -> bool:
    return abs(float(y_new) - float(y_orig) - 0.1) < 0.02


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
