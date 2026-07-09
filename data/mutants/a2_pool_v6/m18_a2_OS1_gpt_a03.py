import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]], dtype=float)
    _, _, U = lu(A)
    diag_vals = np.diag(U)
    return float(np.sum(diag_vals))