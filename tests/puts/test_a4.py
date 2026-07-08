import numpy as np
from p2.puts.a4 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_analytic_value():
    # I(x) = 2x + 1/3, exact for 16-node Gauss-Legendre
    assert abs(program(0.5) - (2 * 0.5 + 1 / 3)) < 1e-9


def test_conservation():
    for x in [0.2, 0.5, 0.75]:
        assert abs(program(x) + program(1 - x) - 8 / 3) < 1e-9
