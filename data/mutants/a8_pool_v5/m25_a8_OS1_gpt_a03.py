_T_END = 1.0
_N_STEPS = 20
_H = _T_END / _N_STEPS


def _rhs(u):
    return u


def program(x) -> float:
    u = 2.0 * float(x) - 1.0
    steps_done = 0
    total = _N_STEPS
    while steps_done != total:
        k1 = _rhs(u)
        k2 = _rhs(u + _H * k1 * 0.5)
        k3 = _rhs(u + _H * k2 * 0.5)
        k4 = _rhs(u + _H * k3)
        u = u + (_H / 6.0) * (k1 + 2.0 * (k2 + k3) + k4)
        steps_done = steps_done + 1
    return float(u)