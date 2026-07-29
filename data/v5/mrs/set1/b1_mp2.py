"""v5 held-out MR — set 1 (gemini-3.5-flash), b1 MP2, candidate 1/3."""
import numpy as np


def r(x):
    return min(float(x) + 0.05, 1.0)


def R(y_orig, y_new):
    return bool(np.isfinite(y_orig) and np.isfinite(y_new) and y_new >= y_orig)
