import numpy as np
from p2.lrca.l3_assumption import is_assumption_violated


def test_iid_holds_for_independent_normal():
    rng = np.random.default_rng(42)
    samples = rng.normal(size=100)
    assert is_assumption_violated(samples) is False


def test_assumption_violated_for_autocorrelated():
    rho = 0.95
    n = 100
    s = np.zeros(n)
    rng = np.random.default_rng(0)
    for i in range(1, n):
        s[i] = rho * s[i - 1] + rng.normal()
    assert is_assumption_violated(s) is True
