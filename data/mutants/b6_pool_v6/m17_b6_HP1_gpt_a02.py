import numpy as np

seed = 42
sample_count = 30
U = np.random.default_rng(seed).uniform(1e-12, 1.0, sample_count)


def program(x) -> float:
    x = float(x)
    rate = 2.5 - 2.0 * x
    vals = -np.log(U) / rate
    return float(np.mean(vals))