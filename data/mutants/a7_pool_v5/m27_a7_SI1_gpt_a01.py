import numpy as np
from scipy.linalg import solve_banded

_N = 6
_D = np.ones(_N)

def program(x) -> float:
    x = float(x)
    ab = np.zeros((3, _N))
    ab[0, 1:] = -1.0
    ab[1, :] = 2.0
    ab[2, :-1] = 0.0
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), ab, b)
    return float(np.sum(u))