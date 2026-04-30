"""B2 R_mp2 must be strict y_new > y_orig (no -0.3 slack)."""
from p2.mrs.b2 import R_mp2


def test_strict_direction_rejects_equal():
    assert not R_mp2(0.5, 0.5), "equal values must NOT satisfy monotone-strict"


def test_strict_direction_rejects_decrease():
    assert not R_mp2(0.5, 0.49), "decrease must NOT satisfy monotone-strict"


def test_strict_direction_accepts_increase():
    assert R_mp2(0.5, 0.51), "increase must satisfy monotone-strict"
