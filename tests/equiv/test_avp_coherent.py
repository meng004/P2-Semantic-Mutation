import numpy as np
from p2.avp.interface import MR
from p2.equiv.avp_coherent import judge_e1


def test_e1_passes_when_all_mr_agree():
    s = lambda x: x * 2
    sm = lambda x: x * 2  # identical
    mr_set = [
        MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="mr1"),
        MR(r=lambda x: x, R=lambda a, b: True, mp_index=2, name="mr2"),
    ]
    assert judge_e1(s, sm, mr_set, epsilon=1e-6) is True
