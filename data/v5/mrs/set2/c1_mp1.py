"""v5 held-out MR — set 2 (grok-4.5), c1 MP1, candidate 1/3."""
import numpy as np

def r(x):
    return 1.0 - float(x)

def R(y_orig, y_new):
    return abs(float(y_orig) + float(y_new)) <= 0.05
