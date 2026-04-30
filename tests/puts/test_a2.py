import numpy as np
from p2.puts.a2 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(float(y), float)


def test_det_formula():
    # product of U diagonal should equal det(A(x)) = 6 + 3x
    for x in [0.0, 0.3, 0.7, 1.0]:
        assert abs(program(x) - (6 + 3*x)) < 1e-8


def test_conservation():
    for x in [0.1, 0.4, 0.8]:
        assert abs(program(x) + program(1-x) - 15.0) < 1e-6
