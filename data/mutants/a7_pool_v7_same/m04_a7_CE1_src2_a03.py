"""A7: Tridiagonal linear solve — direct banded solver (scalar x∈[0,1] interface).

Library: scipy.linalg.solve_banded (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_banded.html

program(x) where x ∈ [0,1] scalar.
Solves SPD tridiagonal T u = (2x-1)·d, T = tridiag(-1, 2, -1) of size 6, d = ones.
Returns Σu. Linear in x; antisymmetric about ½: Σu(x) + Σu(1-x) = 0.
"""
import numpy as np
from scipy.linalg import solve_banded

_N = 6
_DIAG_VAL = 3.0
_OFF_VAL = -1.0

_AB = np.array([
    np.concatenate([[0.0], np.full(_N - 1, _OFF_VAL)]),   # super-diagonal
    np.full(_N, _DIAG_VAL),                                # main diagonal
    np.concatenate([np.full(_N - 1, _OFF_VAL), [0.0]]),   # sub-diagonal
])
_D = np.ones(_N)


def program(x) -> float:
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))