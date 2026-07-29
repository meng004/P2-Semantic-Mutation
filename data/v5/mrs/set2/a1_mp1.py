"""v5 held-out MR — set 2 (grok-4.5), a1 MP1, candidate 1/3."""
def r(x):
    return 1.0 - float(x)

def R(y_orig, y_new):
    return (y_orig >= 0.0) and (y_new >= 0.0) and (abs(y_orig - y_new) < 1e3)
