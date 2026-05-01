import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    xv = float(x)
    a00 = 2.0 - xv
    row0 = [a00, xv]
    row1 = [0.0, 3.0]
    M = np.array([row0, row1])
    P, L, U = lu(M)
    diag_U = np.diag(U)
    result = 1.0
    for v in diag_U:
        result *= float(v)
    return float(result)