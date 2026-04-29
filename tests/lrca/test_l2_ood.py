import numpy as np
from p2.lrca.l2_ood import is_ood_induced


def test_ood_induced_when_fail_only_outside_valid():
    valid_low, valid_high = 0.0, 1.0
    xs = np.linspace(-2, 2, 100)
    fails = [abs(x) > 1.0 for x in xs]
    valid_mask = [(valid_low <= x <= valid_high) for x in xs]
    assert is_ood_induced(fails, valid_mask) is True


def test_not_ood_induced_when_fail_inside():
    diffs = [True] * 100
    valid_mask = [True] * 100
    assert is_ood_induced(diffs, valid_mask) is False
