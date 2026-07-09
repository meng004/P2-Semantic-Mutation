import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    s = 0.0
    for v in np.diag(U):
        s = s + v
    return float(s)