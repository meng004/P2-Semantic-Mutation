import numpy as np
from p2.puts.b6 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_positive_mean():
    for x in [0.0, 0.5, 1.0]:
        assert program(x) > 0.0


def test_monotone_increasing():
    vals = [program(x) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
