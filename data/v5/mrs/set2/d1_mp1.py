"""v5 held-out MR — set 2 (grok-4.5), d1 MP1, candidate 2/3."""
def r(x):
    x = float(x)
    return max(0.0, min(1.0, x * (1.0 - 1e-6)))

def R(y_orig, y_new):
    return abs(float(y_orig) - float(y_new)) < 0.005
