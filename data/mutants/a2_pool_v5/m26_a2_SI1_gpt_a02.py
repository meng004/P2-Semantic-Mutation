import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]], dtype=float)
    _, _, U = lu(A)
    subdiag = np.diag(U, k=-1)
    return float(np.prod(subdiag))