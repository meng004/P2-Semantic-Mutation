import numpy as np
from p2.puts.d2 import program


def test_output_float():
    assert 0 <= float(program(0.5)) <= 1


def test_near_center_high_prob():
    # x=1 → feature [0, 0] → center → high P(y=1)
    assert float(program(1.0)) > 0.8


def test_monotone():
    # SVM probabilities saturate at 1.0 inside the circle; use non-strict monotone
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
    assert vals[-1] > vals[0]  # overall increase is strict
