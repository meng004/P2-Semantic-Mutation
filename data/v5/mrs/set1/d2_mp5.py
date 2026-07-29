"""v5 held-out MR — set 1 (gemini-3.5-flash), d2 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x closer to 1.0, which is the asymptotic regime where the output increases.
    # For x in [0, 1], x + 0.25 * (1.0 - x) is also in [0, 1] and strictly greater than x (for x < 1).
    return float(x + 0.25 * (1.0 - x))


def R(y_orig, y_new):
    # Since r(x) >= x, the output (probability) should increase or stay equal.
    return y_new >= y_orig - 1e-9
