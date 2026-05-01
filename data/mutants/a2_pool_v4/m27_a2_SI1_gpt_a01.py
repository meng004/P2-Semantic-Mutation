import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    value = float(x)
    matrix = np.array([[2.0 + value, value], [0.0, 3.0]], dtype=float)
    _, _, upper = lu(matrix)
    subdiag = np.diag(upper, k=-1)
    result = np.prod(subdiag)
    return float(result)