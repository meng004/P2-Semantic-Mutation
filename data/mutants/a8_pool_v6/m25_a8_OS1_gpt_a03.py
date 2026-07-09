_T_END = 1.0
_N_STEPS = 20

_rhs = lambda u: u


def program(x) -> float:
    u = 2.0 * float(x) - 1.0
    h = _T_END / _N_STEPS
    for _ in range(_N_STEPS):
        k1 = _rhs(u)
        k2 = _rhs(u + 0.5 * h * k1)
        k3 = _rhs(u + 0.5 * h * k2)
        k4 = _rhs(u + h * k3)
        u = u + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return float(u)