import numpy as np


def program(x) -> float:
    x = float(x)
    rng = np.random.default_rng(42)
    props = rng.uniform(-3.0, 3.0, 6000)
    us = rng.uniform(0.0, 1.0, 6000)
    accept = us < np.exp(-0.5 * (props + (4.0 * x - 2.0)) ** 2)
    return float(np.mean(props[accept]))