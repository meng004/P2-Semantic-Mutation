import numpy as np
from scipy.linalg import lu


def build_matrix(t):
    top_left = 2.0 - t
    top_right = t
    return np.array([[top_left, top_right], [0.0, 3.0]])


def program(x) -> float:
    t = float(x)
    A = build_matrix(t)
    _, _, U = lu(A)
    n = U.shape[0]
    acc = 1.0
    idx = 0
    while idx < n:
        acc = acc * float(U[idx, idx])
        idx += 1
    return float(acc)