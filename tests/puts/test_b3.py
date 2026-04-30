import numpy as np
from p2.puts.b3 import program


def test_output_float():
    assert isinstance(float(program(0.0)), float)


def test_near_true_value():
    val = program(0.5)
    assert abs(val - (0.5 + 1.0/3)) < 0.02


def test_linearity():
    for x in [0.0, 0.3, 0.6]:
        diff = program(x + 0.1) - program(x)
        assert abs(diff - 0.1) < 0.02
