"""v5 held-out MR — set 1 (gemini-3.5-flash), b1 MP4, candidate 1/3."""
import numpy as np


def r(x):
    x_clipped = max(0.0, min(1.0, float(x)))
    return round(100.0 * x_clipped) / 100.0


def R(y_orig, y_new):
    return abs(y_orig - y_new) < 1e-6
