import numpy as np
from p2.puts.b7 import program


def test_output_scalar():
    y = program(0.5)
    assert isinstance(y, float) and np.isfinite(y)


def test_deterministic():
    assert program(0.3) == program(0.3)


def test_monotone_in_target_mean():
    assert program(0.8) > program(0.2)


def test_tracks_target_roughly():
    # IS estimate of E_p[t] with target mean 4x-2
    assert abs(program(0.5) - 0.0) < 0.5
