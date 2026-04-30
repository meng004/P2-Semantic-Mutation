import numpy as np
import pytest
from p2.puts.a1 import program as p_a1
from p2.puts.a2 import program as p_a2
from p2.puts.a3 import program as p_a3
import p2.mrs.a1 as mrs_a1
import p2.mrs.a2 as mrs_a2
import p2.mrs.a3 as mrs_a3


def test_a1_r_mp1_in_range():
    for x in [0.1, 0.5, 0.9]:
        xp = mrs_a1.r_mp1(x)
        assert 0.0 <= xp <= 1.0


def test_a2_conservation_mr():
    for x in [0.2, 0.5, 0.8]:
        y_orig = p_a2(x)
        y_new = p_a2(mrs_a2.r_mp1(x))
        assert mrs_a2.R_mp1(y_orig, y_new)


def test_a3_trivial_mr_always_passes():
    for x in [0.1, 0.5, 0.9]:
        y_orig = p_a3(x)
        y_new = p_a3(mrs_a3.r_trivial(x))
        assert mrs_a3.R_trivial(y_orig, y_new)
