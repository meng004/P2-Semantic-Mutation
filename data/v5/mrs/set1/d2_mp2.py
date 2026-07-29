"""v5 held-out MR — set 1 (gemini-3.5-flash), d2 MP2, candidate 1/3."""
import math


def r(x):
    return float(0.5 * x + 0.5)


def R(y_orig, y_new):
    if not math.isfinite(y_orig) or not math.isfinite(y_new):
        return False
    return y_new >= y_orig
