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
_AB = np.zeros((3, _N))
_AB[0, 1:] = -1.0    # super-diagonal
_AB[1, :] = 2.0      # main diagonal
_AB[2, :-1] = 0.0    # sub-diagonal (operator: set to 0.0)
_D = np.ones(_N)


def program(x) -> float:
    x = float(x)
    b = (2.0 * x - 1.0) * _D
    u = solve_banded((1, 1), _AB, b)
    return float(np.sum(u))