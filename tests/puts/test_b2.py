import numpy as np
from p2.puts.b2 import program


def test_output_float():
    assert isinstance(float(program(0.5)), float)


def test_at_center_near_zero():
    val = program(0.5)
    assert abs(val) < 0.5


def test_monotone_coarse():
    assert program(0.7) > program(0.3)
