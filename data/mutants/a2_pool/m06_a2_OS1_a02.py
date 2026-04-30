import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    xv = float(x)
    M = np.array([[2.0 + xv, xv], [0.0, 3.0]])
    _, _, U_factor = lu(M)
    acc = 0.0
    for val in np.diag(U_factor):
        acc += val
    return float(acc)