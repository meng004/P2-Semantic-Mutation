"""v5 held-out MR — set 1 (gemini-3.5-flash), a2 MP1, candidate 1/3."""
import math


def r(x):
    return 1.0 - float(x)


def R(y_orig, y_new):
    return math.isclose(y_orig + y_new, 15.0, rel_tol=1e-9, abs_tol=1e-9)
