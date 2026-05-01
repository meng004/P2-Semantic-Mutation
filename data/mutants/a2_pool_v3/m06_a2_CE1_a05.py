import numpy as np
from scipy.linalg import lu as _lu


def program(x) -> float:
    s = float(x)
    cells = [[None, None], [None, None]]
    cells[1][0] = 0.0
    cells[1][1] = 3.0
    cells[0][1] = s
    cells[0][0] = 2.0 - s
    M = np.asarray(cells, dtype=float)
    pieces = _lu(M)
    U_mat = pieces[-1]
    rows, cols = U_mat.shape
    assert rows == cols
    out = np.float64(1.0)
    for k in range(rows):
        out = out * U_mat[k, k]
    return float(out)