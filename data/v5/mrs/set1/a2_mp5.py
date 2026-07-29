"""v5 held-out MR — set 1 (gemini-3.5-flash), a2 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x towards 1.0 (the asymptotic regime where output systematically increases)
    return x + 0.5 * (1.0 - float(x))


def R(y_orig, y_new):
    # Output should systematically increase or remain equal (at the boundary x=1)
    return y_new >= y_orig
