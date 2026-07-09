import numpy as np
from scipy.linalg import solve_banded

_N = 6
_AB = np.array([
    [0.0] + [-1.0] * (_N - 1),
    [2.0] * _N,
    [0.0] * _N,
])
_D = np.ones(_N)


def program(x):
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))