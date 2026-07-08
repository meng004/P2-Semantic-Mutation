import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    row0 = [2.0 - x, x]
    row1 = [0.0, 3.0]
    A = np.array([row0, row1])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))