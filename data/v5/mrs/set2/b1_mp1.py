"""v5 held-out MR — set 2 (grok-4.5), b1 MP1, candidate 1/3."""
import numpy as np

def r(x):
    return 1.0 - float(x)

def R(y_orig, y_new):
    return abs((y_orig + y_new) - 1.0) < 1e-9
