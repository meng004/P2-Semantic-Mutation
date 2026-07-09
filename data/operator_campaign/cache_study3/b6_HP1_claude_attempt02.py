import numpy as np

_RNG = np.random.default_rng(42)
_U = _RNG.uniform(1e-12, 1.0, 30)


def program(x) -> float:
    xf = float(x)
    lam = 2.5 - 2.0 * xf
    draws = -np.log(_U) / lam
    return float(draws.mean())