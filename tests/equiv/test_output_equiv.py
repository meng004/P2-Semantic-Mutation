import numpy as np
from p2.equiv.output_equiv import judge_e2


def test_e2_passes_for_identical():
    f = lambda x: x * 2
    samples = np.array([[0.1], [0.5], [0.9]])
    assert judge_e2(f, f, samples, epsilon=1e-9) is True


def test_e2_fails_for_divergent():
    f = lambda x: x * 2
    g = lambda x: x * 2 + 1.0
    samples = np.array([[0.1], [0.5], [0.9]])
    assert judge_e2(f, g, samples, epsilon=1e-9) is False
