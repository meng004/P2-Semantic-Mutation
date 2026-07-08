def program(x) -> float:
    T_END = 1.0
    N = 20
    h = T_END / N
    u = 2.0 * float(x) - 1.0
    remaining = N
    while remaining > 0:
        k1 = u
        k2 = (u + 0.5 * h * k1)
        k3 = (u + 0.5 * h * k2)
        k4 = (u + h * k3)
        u = u + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        remaining -= 1
    return float(u)