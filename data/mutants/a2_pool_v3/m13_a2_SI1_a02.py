import numpy as np
from scipy.linalg import lu
from functools import reduce
import operator


def program(x) -> float:
    scalar = float(x)
    mat = np.array([[2.0 + scalar, scalar], [0.0, 3.0]])
    decomposition = lu(mat)
    upper = decomposition[2]
    off_diag_entries = [float(v) for v in np.diag(upper, k=-1)]
    result = reduce(operator.mul, off_diag_entries, 1.0)
    return float(result)