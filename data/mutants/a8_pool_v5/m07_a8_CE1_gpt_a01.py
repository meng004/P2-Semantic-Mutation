T = 1.0
STEPS = 20


def deriv(y):
    return -y


def program(x) -> float:
    dt = T / STEPS
    val = 2.0 * float(x) - 0.5
    for _n in list(range(STEPS)):
        s1 = deriv(val)
        s2 = deriv(val + dt * s1 / 2.0)
        s3 = deriv(val + dt * s2 / 2.0)
        s4 = deriv(val + dt * s3)
        val += dt * (s1 + 2.0 * s2 + 2.0 * s3 + s4) / 6.0
    return float(val)