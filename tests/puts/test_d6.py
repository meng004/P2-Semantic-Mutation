import numpy as np
from p2.puts.d6 import program


def test_output_float():
    assert 0 <= float(program(0.5)) <= 1


def test_center_more_positive_than_edge():
    # x=1 → feature at circle centre (positive); x=0 → outside
    assert float(program(1.0)) > float(program(0.0))


def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
