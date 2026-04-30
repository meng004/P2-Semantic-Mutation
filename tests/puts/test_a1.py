import numpy as np
import pytest
from p2.puts.a1 import program


def test_output_shape():
    y = program(0.5)
    assert isinstance(y, np.ndarray) and y.shape == (10,)


def test_deterministic():
    assert np.allclose(program(0.3), program(0.3))


def test_bounded_trajectory():
    # Lorenz attractor is bounded; x-component stays within [-25, 25] for t ∈ [0,1]
    y = program(0.5)
    assert np.all(np.abs(y) < 25.0)
