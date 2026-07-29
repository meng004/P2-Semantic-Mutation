"""v5 held-out MR — set 2 (grok-4.5), c1 MP4, candidate 1/3."""
import numpy as np

def r(x):
    x = float(x)
    return float(np.clip(x + 1e-10, 0.0, 1.0))

def R(y_orig, y_new):
    return abs(float(y_orig) - float(y_new)) <= 1e-6
