def program(x) -> float:
    end_time = 1.0
    num_steps = 20
    h = end_time / num_steps

    def rhs(w):
        return -w

    u = 2.0 * float(x) - 1.0
    for _idx in range(num_steps - 1):
        m1 = rhs(u)
        m2 = rhs(u + h * m1 / 2.0)
        m3 = rhs(u + h * m2 / 2.0)
        m4 = rhs(u + h * m3)
        u = u + h * (m1 + 2.0 * m2 + 2.0 * m3 + m4) / 6.0
    return float(u)