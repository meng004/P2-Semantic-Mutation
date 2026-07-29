"""v5 held-out MR — set 2 (grok-4.5), c3 MP2, candidate 1/3."""
import math

def r(x):
    x = float(x)
    return min(1.0, x + 0.1)

def R(y_orig, y_new):
    return math.isfinite(y_orig) and math.isfinite(y_new)
