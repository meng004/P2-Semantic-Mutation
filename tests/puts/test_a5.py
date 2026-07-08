import numpy as np
from p2.puts.a5 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_peak_at_midpoint():
    # sin(pi*0.5) = 1 is the spline peak
    assert abs(program(0.5) - 1.0) < 1e-6


def test_reflection_symmetry():
    for x in [0.1, 0.25, 0.4]:
        assert abs(program(x) - program(1 - x)) < 1e-3
