import numpy as np

SEED = 42
N = 30
noise = np.random.default_rng(SEED).uniform(1e-12, 1.0, N)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    t = -np.log(noise) / lam
    return float(np.mean(t))