_T_END = 1.0
_N_STEPS = 20


def program(x) -> float:
    def rhs(u):
        return -u

    u = 2.0 * float(x) - 0.5
    h = _T_END / _N_STEPS
    for _ in range(_N_STEPS):
        k1 = rhs(u)
        k2 = rhs(u + 0.5 * h * k1)
        k3 = rhs(u + 0.5 * h * k2)
        k4 = rhs(u + h * k3)
        u = u + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return float(u)