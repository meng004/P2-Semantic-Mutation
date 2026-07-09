import numpy as np


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 1.0
    rng = np.random.default_rng(42)
    props = rng.uniform(-3.0, 3.0, 6000)
    us = rng.uniform(0.0, 1.0, 6000)
    accept = np.exp(-0.5 * (props - mu) ** 2) > us
    return float(props[accept].mean())