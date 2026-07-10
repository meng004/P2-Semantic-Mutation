"""Python-side reference for XL program 'besselj0' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import j0 as _j0


def program(x) -> float:
    return float(_j0(8.0 * float(x) - 4.0))
