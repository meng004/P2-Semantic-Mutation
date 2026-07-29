"""v5 held-out MR — set 2 (grok-4.5), c1 MP5, candidate 1/3."""
def r(x):
    x = float(x)
    return 1.0 - 0.15 * (1.0 - x)

def R(y_orig, y_new):
    return y_new >= y_orig - 1e-12
