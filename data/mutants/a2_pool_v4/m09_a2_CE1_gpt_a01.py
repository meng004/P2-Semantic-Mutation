import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    a00 = 2.0 - x
    A = np.array([[a00, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))