"""v5 held-out MR — set 2 (grok-4.5), a2 MP2, candidate 1/3."""
import math

def r(x):
    x = float(x)
    return 0.5 * x + 0.5

def R(y_orig, y_new):
    return math.isfinite(y_orig) and math.isfinite(y_new)
