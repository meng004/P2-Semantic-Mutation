import numpy as np
from scipy.linalg import lu
from functools import reduce
import operator


def program(x) -> float:
    x_val = float(x)
    matrix = np.array([[2.0 + x_val, x_val], [0.0, 3.0]])
    P, L, U = lu(matrix)
    diag_entries = np.diag(U)
    total = reduce(operator.add, diag_entries)
    return float(total)