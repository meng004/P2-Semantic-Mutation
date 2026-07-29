"""v5 held-out MR — set 2 (grok-4.5), a3 MP1, candidate 2/3."""
def r(x):
    return min(1.0, 2.0 * float(x))

def R(y_orig, y_new):
    return abs(y_orig - y_new) < 0.1
