import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    base = 2.0
    A = np.array([[base - x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    result = np.prod(np.diag(U))
    return float(result)