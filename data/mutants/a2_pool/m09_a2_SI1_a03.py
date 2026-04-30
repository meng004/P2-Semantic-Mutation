import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    xv = float(x)
    M = np.array([[2.0 + xv, xv], [0.0, 3.0]])
    pieces = lu(M)
    U_mat = pieces[-1]
    total = 1.0
    for idx, value in enumerate(np.diag(U_mat, k=-1)):
        total = total * float(value)
    return float(total)