_T_END = 1.0
_N_STEPS = 20


def _rhs(y):
    return -y


def program(x) -> float:
    u = float(x) * 2.0 - 0.5
    dt = _T_END / _N_STEPS
    for _ in range(_N_STEPS):
        s1 = _rhs(u)
        s2 = _rhs(u + 0.5 * dt * s1)
        s3 = _rhs(u + 0.5 * dt * s2)
        s4 = _rhs(u + dt * s3)
        u = u + dt / 6.0 * (s1 + 2.0 * s2 + 2.0 * s3 + s4)
    return float(u)