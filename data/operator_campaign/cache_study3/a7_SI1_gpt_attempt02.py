import numpy as np
from scipy.linalg import solve_banded

_N = 6
_AB = np.zeros((3, _N))
for _i in range(_N):
    _AB[1, _i] = 2.0
    if _i > 0:
        _AB[0, _i] = -1.0
_D = np.ones(_N)


def program(x):
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))