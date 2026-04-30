# Mutant: compute determinant directly via np.linalg.det instead of LU.
# Expected: EQUIV. np.linalg.det([[2+x,x],[0,3]]) = (2+x)*3 = 6+3x, same value.
import numpy as np


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    return float(np.linalg.det(A))
