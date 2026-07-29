"""v5 held-out MR — set 1 (gemini-3.5-flash), a3 MP1, candidate 1/3."""
import math
import numpy as np

def r(x):
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    return 1.0 / N

def R(y_orig, y_new):
    return math.isclose(y_orig, y_new, rel_tol=1e-11, abs_tol=1e-11)
