# Mutant: add constant offset to output.
# Expected: KILLED by MP1. (6+3x+0.5)+(9-3x+0.5)=16 ≠ 15.
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U))) + 0.5
