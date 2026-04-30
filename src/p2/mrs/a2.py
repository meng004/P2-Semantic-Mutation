"""MR functions for A2 LU Decomposition.

Primary MP: MP1 (Conservation).
  r_mp1(x) = 1 − x  (complement in [0,1]).
  R_mp1: |det(A(x)) + det(A(1-x)) − 15| < 0.01 (determinant sum is conserved).
Trivial: r_trivial (identity), R_trivial for MP2/3/4/5.
"""


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return abs(float(y_orig) + float(y_new) - 15.0) < 0.01


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
