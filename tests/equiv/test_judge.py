from p2.avp.interface import MR
from p2.equiv.judge import is_equivalent
from p2.equiv.sampler import UniformSampler


def test_judge_requires_both_e1_e2():
    s = lambda x: x * 2
    sm = lambda x: x * 2
    mr_set = [MR(lambda x: x, lambda a, b: True, 1, "m")]
    sampler = UniformSampler(0, 1, 1, seed=42)
    assert is_equivalent(s, sm, mr_set, sampler, k_eq=10, epsilon_eq=1e-9, epsilon_avp=1e-6)
