"""PUT e2 (yan2024 Dirichlet five-point Poisson). Fault F2: sign flip on the east off-diagonal coefficient A[k, idx(i,j+1)] (+1/h^2 instead of -1/h^2), breaking the y-direction Laplacian coupling."""
import numpy as np


def _solve_dirichlet_elliptic(N: int) -> np.ndarray:
    """Five-point Dirichlet Poisson solve on (0,1)^2 with seeded F2 fault."""
    h = 1.0 / N
    m = N - 1
    x = (np.arange(1, N)) * h
    y = (np.arange(1, N)) * h
    X, Y = np.meshgrid(x, y, indexing="ij")
    f = 2.0 * np.pi**2 * np.sin(np.pi * X) * np.sin(np.pi * Y)
    M = m * m
    A = np.zeros((M, M))
    b = np.zeros(M)

    def idx(i, j):
        return i * m + j

    for i in range(m):
        for j in range(m):
            k = idx(i, j)
            A[k, k] = 4.0 / h**2
            b[k] = f[i, j]
            if i > 0:
                A[k, idx(i - 1, j)] = -1.0 / h**2
            if i < m - 1:
                A[k, idx(i + 1, j)] = -1.0 / h**2
            if j > 0:
                A[k, idx(i, j - 1)] = -1.0 / h**2
            if j < m - 1:
                # F2 sign flip: should be -1.0 / h**2
                A[k, idx(i, j + 1)] = +1.0 / h**2
    u = np.linalg.solve(A, b)
    return u.reshape(m, m)


def _probe_center(u: np.ndarray, N: int) -> float:
    c = N // 2 - 1
    if c < 0:
        c = 0
    return float(u[c, c])


def program(x) -> float:
    """Observable: Cauchy self-convergence ratio U_N(0.5,0.5)/U_2N(0.5,0.5)."""
    N = int(x)
    uN = _solve_dirichlet_elliptic(N)
    u2N = _solve_dirichlet_elliptic(2 * N)
    return float(_probe_center(uN, N) / _probe_center(u2N, 2 * N))


if __name__ == "__main__":
    for N in (8, 16, 32):
        print(N, program(N))
