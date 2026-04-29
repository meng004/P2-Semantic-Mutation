import math
import numpy as np
from p2.stats.rq4_correlation import spearman_kendall


def test_perfect_positive_correlation():
    sms = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    cov = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    s, k = spearman_kendall(sms, cov)
    assert math.isclose(s, 1.0) and math.isclose(k, 1.0)
