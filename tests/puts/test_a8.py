import numpy as np
from p2.puts.a8 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_antisymmetric_and_bounded():
    assert abs(program(0.5)) < 1e-9
    for x in [0.1, 0.3, 0.4]:
        assert abs(program(x) + program(1 - x)) < 1e-9
    for x in np.linspace(0.0, 1.0, 11):
        assert abs(program(x)) < 0.4


def test_rk4_accuracy_at_x1():
    # u(0)=1, exact u(1)=e^-1; RK4 is 4th-order accurate
    assert abs(program(1.0) - np.exp(-1.0)) < 1e-5
