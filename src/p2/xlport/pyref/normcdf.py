"""Python-side reference for XL program 'normcdf' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import ndtr as _ndtr


def program(x) -> float:
    return float(_ndtr(6.0 * float(x) - 3.0))
