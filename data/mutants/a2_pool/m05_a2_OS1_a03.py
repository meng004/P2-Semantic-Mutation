import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    xf = float(x)
    mat = np.array([[2.0 + xf, xf], [0.0, 3.0]])
    decomp = lu(mat)
    U_mat = decomp[2]
    diag_vals = [U_mat[i, i] for i in range(U_mat.shape[0])]
    result = np.add.reduce(np.asarray(diag_vals))
    return float(result)