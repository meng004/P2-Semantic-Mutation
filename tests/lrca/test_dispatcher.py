from p2.avp.interface import MR
from p2.lrca.dispatcher import LRCALabel, classify_mutant


def test_artifact_short_circuits():
    def m(x): return float("nan")
    def orig(x): return float(x)
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="t")
    assert classify_mutant(m, orig, mr, was_killed=True) == LRCALabel.ARTIFACT


def test_unkilled_returns_survived():
    def m(x): return float(x) + 0.5
    def orig(x): return float(x)
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="t")
    assert classify_mutant(m, orig, mr, was_killed=False) == LRCALabel.SURVIVED


def test_legit_killed_returns_c1():
    def m(x): return float(x) * 2.0
    def orig(x): return float(x)
    mr = MR(r=lambda x: x + 0.1,
            R=lambda a, b: abs(b - a - 0.1) < 1e-9,
            mp_index=1, name="t")
    label = classify_mutant(m, orig, mr, was_killed=True)
    assert label == LRCALabel.C1_LEGIT
