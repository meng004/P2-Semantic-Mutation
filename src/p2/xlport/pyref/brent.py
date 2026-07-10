"""Python-side reference for XL program 'brent' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.optimize import brentq as _brentq


def program(x) -> float:
    c = 4.0 * float(x) - 2.0
    return float(_brentq(lambda t: t * t * t + t - c, -2.0, 2.0, xtol=1e-12))
