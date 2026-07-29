"""v5 held-out MR — set 2 (grok-4.5), b3 MP1, candidate 1/3."""
import numpy as np

def r(x):
    return 1.0 - float(x)

def R(y_orig, y_new):
    return abs(y_orig + y_new - 5.0/3.0) < 0.05
