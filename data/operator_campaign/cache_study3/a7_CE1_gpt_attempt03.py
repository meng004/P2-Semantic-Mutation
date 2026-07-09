import numpy as np
from scipy.linalg import solve_banded

_N = 6
_AB = np.zeros((3, _N))
_AB[0, 1:] = -1.0
_AB[1, :] = 3.0 * np.ones(_N)
_AB[2, :-1] = -1.0
_D = np.ones(_N)


def program(x):
    xv = float(x)
    forcing = (2.0 * xv - 1.0) * _D
    solution = solve_banded((1, 1), _AB, forcing)
    return float(np.add.reduce(solution))