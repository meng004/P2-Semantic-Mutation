_T_END = 1.0
_N_STEPS = 20


def _step(u, h):
    k1 = -1.0 * u
    k2 = -1.0 * (u + 0.5 * h * k1)
    k3 = -1.0 * (u + 0.5 * h * k2)
    k4 = -1.0 * (u + h * k3)
    return u + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def program(x) -> float:
    u = 2.0 * float(x) - 1.0
    h = _T_END / _N_STEPS
    for _ in range(19):
        u = _step(u, h)
    return float(u)