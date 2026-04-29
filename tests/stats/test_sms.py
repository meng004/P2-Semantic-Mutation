import math
from p2.stats.sms import compute_sms


def test_sms_basic():
    sms = compute_sms(killed=10, total=20, equiv=5)
    assert math.isclose(sms, 10.0 / 15.0)


def test_sms_zero_when_none_killed():
    sms = compute_sms(killed=0, total=10, equiv=5)
    assert sms == 0.0


def test_sms_undefined_returns_nan():
    sms = compute_sms(killed=0, total=5, equiv=5)
    assert math.isnan(sms)
