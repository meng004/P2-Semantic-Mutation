"""v5 held-out MR — set 1 (gemini-3.5-flash), c1 MP2, candidate 1/3."""
import numpy as np


def r(x):
    # Monotonically increase the input x within the valid domain [0, 1]
    return x + 0.1 * (1.0 - x)


def R(y_orig, y_new):
    # Verify both outputs are valid finite numbers
    return np.isfinite(y_orig) and np.isfinite(y_new)
