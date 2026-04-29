"""A2: LU Decomposition — numerical linear algebra.

Library: scipy.linalg.lu (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html

program(x) where x is flat 1D array of n² elements representing square matrix A.
Returns flat concatenation of L and U (each n×n), shape (2n²,).
Pivot matrix P is discarded; caller is responsible for non-singular input.
"""
import numpy as np
from scipy.linalg import lu


def program(x: np.ndarray) -> np.ndarray:
    """Compute LU decomposition of square matrix encoded in x; return flat [L; U]."""
    x = np.asarray(x, dtype=float)
    n = int(round(len(x) ** 0.5))
    A = x.reshape(n, n)
    _, L, U = lu(A)
    return np.concatenate([L.ravel(), U.ravel()])  # shape (2n²,)
