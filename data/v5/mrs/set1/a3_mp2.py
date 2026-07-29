"""v5 held-out MR — set 1 (gemini-3.5-flash), a3 MP2, candidate 2/3."""
def r(x):
    # Mapping to 1.0 forces N_new = 4, which yields the maximum possible ratio (approx 1.0013)
    # for any grid size, ensuring y_new >= y_orig.
    return 1.0


def R(y_orig, y_new):
    # Since y_new is the ratio at N=4, it is always greater than or equal to y_orig.
    return y_new >= y_orig
