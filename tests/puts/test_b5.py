import numpy as np
from p2.puts.b5 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_bounded_support():
    for x in [0.0, 0.5, 1.0]:
        assert -3.0 <= program(x) <= 3.0


def test_monotone_in_target_mean():
    assert program(0.8) > program(0.2)
