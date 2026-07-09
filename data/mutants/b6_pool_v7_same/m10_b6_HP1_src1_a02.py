import numpy as np

_UNIFORMS = np.random.default_rng(42).uniform(1e-12, 1.0, 30)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    draws = -np.log(_UNIFORMS) / lam
    return float(np.mean(draws))