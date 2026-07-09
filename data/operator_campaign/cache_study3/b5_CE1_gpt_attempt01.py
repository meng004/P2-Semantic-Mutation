"""B5: truncated-Gaussian rejection Monte-Carlo (mutant)."""
import numpy as np

SEED = 42
NPROP = 6000
LOW, HIGH = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 1.0
    gen = np.random.default_rng(SEED)
    props = gen.uniform(LOW, HIGH, NPROP)
    us = gen.uniform(0.0, 1.0, NPROP)
    kernel = np.exp(-((props - mu) ** 2) / 2.0)
    mask = np.less(us, kernel)
    return float(np.mean(props[mask]))