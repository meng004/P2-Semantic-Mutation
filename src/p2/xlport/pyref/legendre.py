"""Python-side reference for XL program 'legendre' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import eval_legendre as _eval_legendre


def program(x) -> float:
    return float(_eval_legendre(3, 2.0 * float(x) - 1.0))
