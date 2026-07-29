"""v5 held-out MR — set 1 (gemini-3.5-flash), d1 MP1, candidate 2/3."""
import numpy as np


def r(x):
    return float(np.clip(x, 0.0, 1.0))


def R(y_orig, y_new):
    return abs(y_orig - y_new) < 1e-9
