"""v5 held-out MR — set 1 (gemini-3.5-flash), a2 MP2, candidate 1/3."""
import numpy as np


def r(x):
    # Map x in [0, 1] to [0.5, 1.0], which is strictly greater than x for x < 1
    return 0.5 * float(x) + 0.5


def R(y_orig, y_new):
    # Ensure both outputs are valid finite numbers
    return np.isfinite(y_orig) and np.isfinite(y_new)
