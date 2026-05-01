import numpy as np
from scipy.linalg import lu
from functools import reduce
import operator


def program(x) -> float:
    val = float(x)
    entries = {(0, 0): 2.0 - val, (0, 1): val, (1, 0): 0.0, (1, 1): 3.0}
    A = np.array([[entries[(0, 0)], entries[(0, 1)]],
                  [entries[(1, 0)], entries[(1, 1)]]])
    P, L, U = lu(A)
    u_diag = [float(U[i, i]) for i in range(U.shape[0])]
    product = reduce(operator.mul, u_diag, 1.0)
    return float(product)