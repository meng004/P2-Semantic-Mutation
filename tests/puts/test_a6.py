import numpy as np
from p2.puts.a6 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_root_satisfies_equation():
    for x in [0.2, 0.5, 0.8]:
        r = program(x)
        assert abs(r**3 + r - (4 * x - 2)) < 1e-8


def test_odd_symmetry_and_monotone():
    assert abs(program(0.5)) < 1e-9
    for x in np.linspace(0.05, 0.9, 9):
        assert program(x + 0.05) > program(x)
    for x in [0.1, 0.3]:
        assert abs(program(x) + program(1 - x)) < 1e-6
