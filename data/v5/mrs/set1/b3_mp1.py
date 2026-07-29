"""v5 held-out MR — set 1 (gemini-3.5-flash), b3 MP1, candidate 1/3."""
import numpy as np

_rng_samples = np.random.default_rng(42).uniform(0.0, 1.0, 5000)
_C = float(np.mean(_rng_samples**2))


def r(x):
    return 0.5 * float(x)


def R(y_orig, y_new):
    return np.isclose(y_new - 0.5 * y_orig, 0.5 * _C, atol=1e-12)
