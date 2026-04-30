"""A1 program(x) must return a finite scalar float."""
import numpy as np
import pytest
from p2.puts.a1 import program


@pytest.mark.parametrize("x", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_returns_scalar_float(x):
    y = program(x)
    assert isinstance(y, float), f"expected float, got {type(y).__name__}"
    assert np.isfinite(y), f"expected finite, got {y}"


def test_two_calls_same_x_are_equal():
    y1 = program(0.4)
    y2 = program(0.4)
    assert y1 == y2, "deterministic ODE must give bitwise identical result"
