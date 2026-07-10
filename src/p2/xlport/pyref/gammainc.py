"""Python-side reference for XL program 'gammainc' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import gammainc as _gammainc


def program(x) -> float:
    return float(_gammainc(2.5, 8.0 * float(x)))
