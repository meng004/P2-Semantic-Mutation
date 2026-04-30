# Mutant: scale output by 1.1.
# Expected: KILLED by MP1. 1.1*(6+3x)+1.1*(9-3x)=1.1*15=16.5 ≠ 15.
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U))) * 1.1
