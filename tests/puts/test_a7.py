import numpy as np
from p2.puts.a7 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_antisymmetric_and_zero_at_mid():
    assert abs(program(0.5)) < 1e-9
    for x in [0.1, 0.3, 0.4]:
        assert abs(program(x) + program(1 - x)) < 1e-9


def test_monotone():
    for x in np.linspace(0.05, 0.9, 9):
        assert program(x + 0.05) > program(x)
