"""v5 held-out MR — set 1 (gemini-3.5-flash), b3 MP5, candidate 1/3."""
def r(x):
    return 0.5 * float(x) + 0.5


def R(y_orig, y_new):
    return y_new >= y_orig
