import numpy as np
from scipy.linalg import lu


def _make_A(p):
    A = np.zeros((2, 2))
    A[0, 0] = 2.0 - p
    A[0, 1] = p
    A[1, 0] = 0.0
    A[1, 1] = 3.0
    return A


def program(x) -> float:
    p = float(x)
    matrix = _make_A(p)
    decomposition = lu(matrix)
    U = decomposition[2]
    diag_vals = np.diagonal(U)
    log_abs = 0.0
    sign = 1.0
    for v in diag_vals:
        fv = float(v)
        if fv == 0.0:
            return 0.0
        sign *= (1.0 if fv > 0.0 else -1.0)
        log_abs += float(np.log(abs(fv)))
    return float(sign * np.exp(log_abs))