import numpy as np
from p2.puts.b1 import program


def test_output_float():
    assert isinstance(float(program(0.5)), float)


def test_monotone():
    for x in np.linspace(0.05, 0.90, 10):
        assert program(x + 0.05) > program(x)


def test_boundary_values():
    assert abs(program(0.0) - 1/102) < 1e-6
    assert abs(program(1.0) - 101/102) < 1e-6
