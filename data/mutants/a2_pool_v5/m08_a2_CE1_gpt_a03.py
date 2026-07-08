import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 - float(x), x], [0.0, 3.0]], dtype=float)
    _, _, U = lu(A)
    diag = np.diag(U)
    return float(np.prod(diag))