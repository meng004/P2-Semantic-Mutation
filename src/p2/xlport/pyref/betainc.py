"""Python-side reference for XL program 'betainc' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import betainc as _betainc


def program(x) -> float:
    return float(_betainc(2.5, 2.5, float(x)))
