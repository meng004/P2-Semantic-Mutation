# Mutant: return sum of U diagonal instead of product.
# Expected: KILLED by MP1. sum_diag = (2+x)+3 = 5+x; (5+x)+(5+1-x) = 11 ≠ 15.
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.sum(np.diag(U)))
