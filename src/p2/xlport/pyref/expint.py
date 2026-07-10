"""Python-side reference for XL program 'expint' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.special import exp1 as _exp1


def program(x) -> float:
    return float(_exp1(0.1 + 3.9 * float(x)))
