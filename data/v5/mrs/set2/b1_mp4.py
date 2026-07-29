"""v5 held-out MR — set 2 (grok-4.5), b1 MP4, candidate 1/3."""
import numpy as np

def r(x):
    x = float(np.clip(x, 0.0, 1.0))
    return round(100 * x) / 100.0

def R(y_orig, y_new):
    return abs(y_orig - y_new) <= 1e-6
