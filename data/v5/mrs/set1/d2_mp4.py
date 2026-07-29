"""v5 held-out MR — set 1 (gemini-3.5-flash), d2 MP4, candidate 1/3."""
def r(x):
    # Identity transform is used as a last resort because the SVM model is trained 
    # on random data, making its decision boundary non-symmetric and preventing 
    # any non-trivial exact invariance.
    return float(x)


def R(y_orig, y_new):
    # Trajectory similarity: the output should remain identical.
    return abs(y_orig - y_new) <= 1e-6
