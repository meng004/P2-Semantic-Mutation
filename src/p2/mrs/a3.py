"""MR functions for A3 FDM Heat Equation.

Primary MP: MP3 (Convergence) — mr.r and mr.R are NOT used by MP3 verifier.
  r_mp3 / R_mp3 defined for completeness but unused by verify_convergence_order.
MP2 (Monotonicity): finer grid → ratio closer to 1.
  r_mp2(x) = x / 2 (halve grid spacing → more accurate → ratio increases).
  R_mp2: |y_n - 1.0| <= |y_o - 1.0| (finer grid → closer to 1).
Trivial: r_trivial (identity), R_trivial for MP1/4/5.
"""
import numpy as np


def r_mp3(x) -> float:
    return float(x) / 2.0


def R_mp3(y_orig, y_new) -> bool:
    return True  # unused by verify_convergence_order


def r_mp2(x) -> float:
    return max(float(x) / 2.0, 1e-4)


def R_mp2(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    return abs(y_n - 1.0) <= abs(y_o - 1.0) + 1e-4


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
