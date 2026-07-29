"""v5 held-out MR — set 1 (gemini-3.5-flash), c2 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x towards 1.0, which is the asymptotic regime where the output increases
    x = float(x)
    return x + 0.1 * (1.0 - x)


def R(y_orig, y_new) -> bool:
    # In the asymptotic regime, the output should increase or remain equal
    return y_new >= y_orig
