"""Python-side reference for XL program 'quad' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md). scipy/numpy reference."""

from scipy.integrate import quad as _quad


def program(x) -> float:
    return float(_quad(lambda u: 1.0 / (1.0 + u * u), 0.0, 4.0 * float(x),
                       epsabs=1e-10, epsrel=1e-10)[0])
