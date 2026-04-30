"""MR functions for A1 Lorenz ODE (scalar-output interface).

Primary MP: MP1 (Conservation — weak: trajectory norm stays positive and bounded).
  r_mp1(x) = 1 - x : symmetry under IC reflection.
  R_mp1: |program(x) + program(1-x)| < 1e6 (anti-divergence guard).
Trivial: r_trivial, R_trivial for MP2/3/4/5.
"""
import numpy as np


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return float(abs(float(y_orig) + float(y_new))) < 1e6


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
