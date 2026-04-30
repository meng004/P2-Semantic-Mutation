# Mutant: symmetric matrix A = [[2+x, x], [x, 3]].
# Expected: KILLED by MP1. det = 3(2+x) - x^2 = 6+3x-x^2, asymmetric sum.
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [x, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))
