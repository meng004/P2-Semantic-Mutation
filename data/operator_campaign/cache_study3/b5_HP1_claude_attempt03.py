import numpy as np


def program(x) -> float:
    seed = 42
    n = 50
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(seed)
    props = rng.uniform(-3.0, 3.0, n)
    us = rng.uniform(0.0, 1.0, n)
    d = props - mu
    accept = us < np.exp(-0.5 * d * d)
    return float(np.mean(props[accept]))