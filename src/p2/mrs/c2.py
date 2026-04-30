"""MR functions for C2 Polynomial Chaos surrogate.
Primary MP: MP5 (Fidelity-order = monotone since tanh is monotone).
  r_mp5(x) = min(x + 0.1, 0.9), R_mp5: y_new > y_orig.
Trivial for MP1/2/3/4.
"""


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
