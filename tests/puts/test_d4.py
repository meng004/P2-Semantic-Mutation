import numpy as np
from p2.puts.d4 import program


def test_output_float():
    assert 0 <= float(program(0.5)) <= 1


def test_positive_class_for_large_x():
    assert float(program(0.9)) > 0.5


def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
