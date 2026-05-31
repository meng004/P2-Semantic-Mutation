"""PUT e1 (yan2024 Neumann elliptic). F1 operator scaling variant: an extra factor of h folded into the second-difference scaling under-scales the discrete Laplacian by h (1/h^2 -> 1/h)."""
import numpy as np


def _exact(x, y):
    return np.cos(np.pi * x) * np.cos(np.pi * y)


def _solve_neumann_elliptic(h):
    n = int(round(1.0 / h)) + 1
    xs = np.linspace(0.0, 1.0, n)
    ys = np.linspace(0.0, 1.0, n)
    # FAULT F1 variant: extra factor of h folded into the second-difference scaling
    # correct inv = 1/h^2; here inv = (1/h^2) * h = 1/h, i.e. operator under-scaled by h
    inv = (1.0 / h ** 2) * h
    T = np.zeros((n, n))
    for i in range(n):
        T[i, i] = 2.0 * inv
        if i > 0:
            T[i, i - 1] = -1.0 * inv
        if i < n - 1:
            T[i, i + 1] = -1.0 * inv
    T[0, 1] = -2.0 * inv
    T[n - 1, n - 2] = -2.0 * inv
    I = np.eye(n)
    A = np.kron(T, I) + np.kron(I, T) + np.eye(n * n)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    U = _exact(X, Y)
    f = (2.0 * np.pi ** 2 + 1.0) * U
    fv = f.reshape(-1)
    Uv = np.linalg.solve(A, fv)
    return xs, ys, Uv.reshape(n, n)


def program(x):
    h = float(x)
    xs, ys, U = _solve_neumann_elliptic(h)
    ix = int(np.argmin(np.abs(xs - 0.25)))
    iy = int(np.argmin(np.abs(ys - 0.25)))
    u_num = U[ix, iy]
    u_ex = _exact(xs[ix], ys[iy])
    return float(u_num / u_ex)
