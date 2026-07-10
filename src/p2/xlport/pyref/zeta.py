"""Python-side reference for XL program 'zeta' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import zeta as _zeta


def program(x) -> float:
    return float(_zeta(2.0 + 3.0 * float(x)))
