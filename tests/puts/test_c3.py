import numpy as np
from p2.puts.c3 import program


def test_output_scalar():
    assert isinstance(float(program(0.5)), float)


def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))


def test_midpoint_near_half():
    # sigmoid(0) = 0.5
    assert abs(float(program(0.5)) - 0.5) < 0.1
