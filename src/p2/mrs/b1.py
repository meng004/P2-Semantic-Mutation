"""MR functions for B1 Beta-Binomial conjugate.

Primary MP: MP2 (Monotonicity).
  r_mp2(x) = min(x + 0.01, 0.99): one more success → higher posterior mean.
  R_mp2(y_orig, y_new): y_new > y_orig.
Trivial: r_trivial, R_trivial for MP1/3/4/5.
"""
import numpy as np


def r_mp2(x) -> float:
    return float(min(float(x) + 0.01, 0.99))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
