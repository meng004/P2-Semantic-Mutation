"""A2: LU Decomposition — conservation of determinant under complement transform.

Library: scipy.linalg.lu (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html

program(x) where x ∈ [0,1] scalar.
Matrix: A(x) = [[2+x, x], [0, 3]]; det(A) = 3(2+x) = 6+3x.
Returns: product of U diagonal = det(A(x)) as scalar float.
Conservation: det(A(x)) + det(A(1-x)) = 15 for all x.
"""
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 - 6.5 * x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))