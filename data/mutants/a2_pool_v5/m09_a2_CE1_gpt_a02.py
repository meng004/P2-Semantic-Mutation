import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.zeros((2, 2))
    A[0, 0] = 2.0 - x
    A[0, 1] = x
    A[1, 1] = 3.0
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))