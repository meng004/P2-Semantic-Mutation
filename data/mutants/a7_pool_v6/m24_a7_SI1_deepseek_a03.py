import numpy as np
from scipy.linalg import solve_banded

_N = 6
_SUB = 0.0
_AB = np.zeros((3, _N))
_AB[0, 1:] = -1.0
_AB[1, :] = 2.0
_AB[2, :-1] = _SUB
_D = np.ones(_N)


def program(x) -> float:
    val = float(x)
    b = (2.0 * val - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))