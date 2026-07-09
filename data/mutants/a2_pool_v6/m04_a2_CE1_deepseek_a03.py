import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0, 0.0], [0.0, 3.0]])
    A[0, 0] = A[0, 0] - x
    A[0, 1] = x
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))