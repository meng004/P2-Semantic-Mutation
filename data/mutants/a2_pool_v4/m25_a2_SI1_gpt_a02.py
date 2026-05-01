import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array(
        [
            [2.0 + x, x],
            [0.0, 3.0],
        ],
        dtype=float,
    )
    P, L, U = lu(A)
    subdiag = np.diag(U, k=-1)
    value = np.prod(subdiag)
    return float(value)