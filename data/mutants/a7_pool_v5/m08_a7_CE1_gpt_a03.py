import numpy as np
from scipy.linalg import solve_banded

_N = 6
_SUP = np.array([0.0] + [-1.0] * (_N - 1))
_MAIN = np.array([3.0] * _N)
_SUB = np.array([-1.0] * (_N - 1) + [0.0])
_AB = np.vstack([_SUP, _MAIN, _SUB])
_D = np.ones(_N)

def program(x) -> float:
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))