import numpy as np
from p2.puts.b4 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_monotone_in_shift():
    vals = [program(x) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
