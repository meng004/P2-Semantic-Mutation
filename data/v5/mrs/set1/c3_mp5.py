"""v5 held-out MR — set 1 (gemini-3.5-flash), c3 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x towards the asymptotic upper bound (1.0) where the output systematically increases
    return float(x + 0.2 * (1.0 - x))


def R(y_orig, y_new):
    # Both outputs should be valid finite numbers
    return np.isfinite(y_orig) and np.isfinite(y_new)
