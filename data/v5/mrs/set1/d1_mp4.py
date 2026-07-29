"""v5 held-out MR — set 1 (gemini-3.5-flash), d1 MP4, candidate 1/3."""
def r(x):
    # Since the MLP classifier's prediction probability is strictly monotonic
    # on [0, 1], there is no non-trivial exact output-preserving input transform.
    # We use the identity transform as the admissible last resort.
    return x


def R(y_orig, y_new):
    # Trajectory similarity: the output should be identical for the identity transform.
    return abs(y_orig - y_new) <= 1e-6
