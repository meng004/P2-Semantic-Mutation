"""MR functions for D1 Linear SVM classifier.
Primary MP: MP2 (Monotonicity: feature [x,x] crosses boundary x1+x2=0).
  r_mp2(x) = min(x + 0.1, 0.9): increases x → higher P(y=1).
  R_mp2: y_new > y_orig - 0.05 (coarse; allow plateau near boundary).
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
