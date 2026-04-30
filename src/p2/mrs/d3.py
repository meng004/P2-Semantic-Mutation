"""MR functions for D3 Decision Tree classifier.
Primary MP: MP2 (Monotonicity: feature [x,0] crosses boundary 0.8x1-0.6x2=0).
  r_mp2(x) = min(x + 0.1, 0.9): increases x → P(y=1) non-decreasing.
  R_mp2: y_new > y_orig - 0.05 (coarse; tree probabilities are step-wise).
Trivial for MP1/3/4/5.
"""


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
