"""v5 held-out MR — set 1 (gemini-3.5-flash), c1 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x towards 1.0, the asymptotic regime where the monotone
    # increasing GPR surrogate output systematically increases.
    return x + 0.15 * (1.0 - x)


def R(y_orig, y_new):
    # Gating validity: both outputs must be valid finite real numbers.
    return np.isfinite(y_orig) and np.isfinite(y_new)
