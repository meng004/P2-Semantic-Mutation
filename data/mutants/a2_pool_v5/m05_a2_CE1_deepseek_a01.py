import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    top_left = 2.0 - x
    A = np.array([[top_left, x], [0.0, 3.0]])
    P, L, U = lu(A)
    return float(np.prod(np.diag(U)))