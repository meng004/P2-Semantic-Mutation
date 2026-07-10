"""Python-side reference for XL program 'erf' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import erf as _erf


def program(x) -> float:
    return float(_erf(4.0 * float(x) - 2.0))
