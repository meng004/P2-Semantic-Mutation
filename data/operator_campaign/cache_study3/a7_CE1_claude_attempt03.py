import numpy as np
from scipy.linalg import solve_banded

_N = 6


def _band():
    ab = np.zeros((3, _N))
    ab[0, 1:] = -1.0
    ab[1, :] = 2.0 + 1.0
    ab[2, :-1] = -1.0
    return ab


def program(x) -> float:
    x = float(x)
    b = (2.0 * x - 1.0) * np.ones(_N)
    u = solve_banded((1, 1), _band(), b)
    return float(np.sum(u))