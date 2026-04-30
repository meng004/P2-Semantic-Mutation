import numpy as np
from p2.puts.a3 import program


def test_ratio_near_one_for_fine_grid():
    ratio = program(0.0125)
    assert abs(ratio - 1.0) < 0.02


def test_convergence_order():
    # error should decrease as h decreases (order ~2)
    e1 = abs(program(0.1) - 1.0)
    e2 = abs(program(0.05) - 1.0)
    e3 = abs(program(0.025) - 1.0)
    assert e2 < e1 and e3 < e2


def test_coarse_grid_further_from_one():
    ratio_coarse = program(0.5)
    ratio_fine = program(0.05)
    assert abs(ratio_fine - 1.0) < abs(ratio_coarse - 1.0)
