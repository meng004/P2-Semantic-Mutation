"""v5 held-out MR — set 1 (gemini-3.5-flash), c2 MP2, candidate 1/3."""
def r(x):
    return x + 0.1 * (1.0 - x)


def R(y_orig, y_new):
    return y_new >= y_orig
