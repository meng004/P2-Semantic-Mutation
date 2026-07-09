_T_END = 1.0
_N_STEPS = 20


def _rhs(u):
    return -u


def _rk4_step(u, h):
    k1 = _rhs(u)
    k2 = _rhs(u + 0.5 * h * k1)
    k3 = _rhs(u + 0.5 * h * k2)
    k4 = _rhs(u + h * k3)
    return u + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def program(x) -> float:
    u = 2.0 * float(x) - 0.5
    h = _T_END / _N_STEPS
    for _ in range(_N_STEPS):
        u = _rk4_step(u, h)
    return float(u)