"""Python-side reference for XL program 'gamma' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import gamma as _gamma


def program(x) -> float:
    return float(_gamma(2.0 + 2.0 * float(x)))
