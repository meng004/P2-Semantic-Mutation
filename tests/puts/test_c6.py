import numpy as np
from p2.puts.c6 import program


def test_output_scalar():
    assert isinstance(float(program(0.5)), float)


def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 9)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))


def test_midpoint_near_zero():
    # erf(0)=0 at t = 6*0.5-3 = 0
    assert abs(float(program(0.5))) < 0.1
