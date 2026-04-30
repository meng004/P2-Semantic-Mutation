import numpy as np
from p2.puts.a1 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float)
    assert np.isfinite(y)


def test_deterministic():
    assert np.isclose(program(0.3), program(0.3))


def test_bounded_norm():
    # L2 norm of Lorenz state is bounded for t ∈ [0,1]
    y = program(0.5)
    assert 0.0 < y < 200.0
