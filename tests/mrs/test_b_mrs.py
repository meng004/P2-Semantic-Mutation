import numpy as np
from p2.puts.b1 import program as p_b1
from p2.puts.b2 import program as p_b2
from p2.puts.b3 import program as p_b3
import p2.mrs.b1 as mrs_b1
import p2.mrs.b2 as mrs_b2
import p2.mrs.b3 as mrs_b3


def test_b1_r_mp2_increases():
    for x in [0.1, 0.4, 0.7]:
        y_orig = p_b1(x)
        y_new = p_b1(mrs_b1.r_mp2(x))
        assert mrs_b1.R_mp2(y_orig, y_new)


def test_b2_r_mp2_increases():
    y1 = p_b2(0.3)
    y2 = p_b2(mrs_b2.r_mp2(0.3))
    assert float(y2) > float(y1) - 0.3


def test_b3_r_mp1_conservation():
    for x in [0.0, 0.3, 0.6]:
        y_orig = p_b3(x)
        y_new = p_b3(mrs_b3.r_mp1(x))
        assert mrs_b3.R_mp1(y_orig, y_new)
