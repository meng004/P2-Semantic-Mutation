import numpy as np
from p2.stats.rq3_cross_class import sign_test_all_positive, cv


def test_sign_test_passes_when_all_positive():
    delta_per_class = {"A": 0.3, "B": 0.4, "C": 0.2, "D": 0.5}
    assert sign_test_all_positive(delta_per_class) is True


def test_cv_calculation():
    delta_per_class = {"A": 0.3, "B": 0.4, "C": 0.2, "D": 0.5}
    val = cv(delta_per_class)
    assert val < 0.5
