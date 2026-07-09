import numpy as np

seed = 42
n = 6000
U = np.random.default_rng(seed).uniform(1e-12, 1.0, n)


def program(x) -> float:
    x = float(x)
    rate = 2.5 - x
    vals = np.negative(np.log(U)) / rate
    return float(np.mean(vals))