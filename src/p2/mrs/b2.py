"""MR functions for B2 MCMC Metropolis-Hastings.

Primary MP: MP2 (Monotonicity).
  r_mp2(x) = min(x + 0.05, 0.95): shifts target mean up by 0.2 → chain mean increases.
  R_mp2: float(y_new) > float(y_orig) - 0.3 (coarse; chain is stochastic).
Trivial: r_trivial, R_trivial for MP1/3/4/5.
"""
import numpy as np


def r_mp2(x) -> float:
    return float(min(float(x) + 0.05, 0.95))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.3


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
