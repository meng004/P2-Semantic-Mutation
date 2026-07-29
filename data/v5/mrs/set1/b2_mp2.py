"""v5 held-out MR — set 1 (gemini-3.5-flash), b2 MP2, candidate 1/3."""
import numpy as np


def r(x):
    # Maps x in [0, 1] to [0.5, 1.0], ensuring r(x) > x for all x < 1.
    return x + 0.5 * (1.0 - x)


def R(y_orig, y_new):
    # For a monotonic increasing function, y_new must be strictly greater than y_orig.
    return np.isfinite(y_orig) and np.isfinite(y_new) and y_new > y_orig
