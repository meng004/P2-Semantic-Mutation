"""Python-side reference for XL program 'multiroot' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

from scipy.optimize import root


def program(x) -> float:
    r = 1.0 + float(x) / 2.0

    def f(p):
        u, v = p
        return [u * u + v * v - r * r, u - v - 0.3]

    res = root(f, [1.0, 0.5], method="hybr", tol=1e-12)
    return float(res.x[0])
