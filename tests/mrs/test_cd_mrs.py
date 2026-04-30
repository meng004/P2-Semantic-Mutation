import numpy as np
from p2.puts.c1 import program as p_c1
from p2.puts.c2 import program as p_c2
from p2.puts.c3 import program as p_c3
from p2.puts.d1 import program as p_d1
from p2.puts.d2 import program as p_d2
from p2.puts.d3 import program as p_d3
import p2.mrs.c1 as mrs_c1
import p2.mrs.c2 as mrs_c2
import p2.mrs.c3 as mrs_c3
import p2.mrs.d1 as mrs_d1
import p2.mrs.d2 as mrs_d2
import p2.mrs.d3 as mrs_d3


def test_c1_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c1.R_mp5(p_c1(x), p_c1(mrs_c1.r_mp5(x)))


def test_c2_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c2.R_mp5(p_c2(x), p_c2(mrs_c2.r_mp5(x)))


def test_c3_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c3.R_mp5(p_c3(x), p_c3(mrs_c3.r_mp5(x)))


def test_d1_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d1.R_mp2(p_d1(x), p_d1(mrs_d1.r_mp2(x)))


def test_d2_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d2.R_mp2(p_d2(x), p_d2(mrs_d2.r_mp2(x)))


def test_d3_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d3.R_mp2(p_d3(x), p_d3(mrs_d3.r_mp2(x)))
