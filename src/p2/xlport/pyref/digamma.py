"""Python-side reference for XL program 'digamma' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import psi as _psi


def program(x) -> float:
    return float(_psi(1.0 + 4.0 * float(x)))
