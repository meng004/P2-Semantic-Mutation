"""B3: Monte Carlo integration — naive MC estimate of ∫_a^b sin(t)² dt.

Library: numpy.random (numpy 2.4.4).
URL: https://numpy.org/doc/stable/reference/random/index.html

True value: (b-a)/2 - (sin(2b) - sin(2a))/4.

program(x) where x = [a, b, log_n] (integration bounds + log10 sample count).
Returns MC estimate using n = round(10^log_n) samples with seed=42.
"""
import numpy as np

_SEED = 42


def program(x: np.ndarray) -> float:
    """Estimate ∫_a^b sin(t)² dt via Monte Carlo; return scalar estimate."""
    x = np.asarray(x, dtype=float)
    a, b, log_n = float(x[0]), float(x[1]), float(x[2])
    n = max(1, int(round(10.0 ** np.clip(log_n, 1.0, 6.0))))
    rng = np.random.default_rng(_SEED)
    t = rng.uniform(a, b, size=n)
    return float((b - a) * np.mean(np.sin(t) ** 2))
