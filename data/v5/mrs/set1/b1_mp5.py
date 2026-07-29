"""v5 held-out MR — set 1 (gemini-3.5-flash), b1 MP5, candidate 1/3."""
import numpy as np


def r(x):
    return float(np.clip(x + 0.05, 0.0, 1.0))


def R(y_orig, y_new):
    return y_new >= y_orig
