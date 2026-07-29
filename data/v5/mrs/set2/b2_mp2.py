"""v5 held-out MR — set 2 (grok-4.5), b2 MP2, candidate 1/3."""
def r(x):
    x = float(x)
    return min(1.0, x + 0.15)

def R(y_orig, y_new):
    return (np.isfinite(y_orig) and np.isfinite(y_new))
