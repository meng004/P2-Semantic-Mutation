import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    value = float(x)
    arr = np.array([[2.0 + value, value], [0.0, 3.0]])
    lu_result = lu(arr)
    upper = lu_result[-1]
    n = upper.shape[0]
    running_total = 0.0
    idx = 0
    while idx < n:
        running_total = running_total + upper[idx, idx]
        idx += 1
    return float(running_total)