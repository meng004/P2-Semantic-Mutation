import numpy as np
from scipy.linalg import solve_banded

_N = 6
_AB = np.zeros((3, _N))
_AB[0, 1:] = -1.0
_AB[1, :] = 2.0
_AB[2, :-1] = np.zeros(_N - 1)
_D = np.ones(_N)

def program(x) -> float:
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))