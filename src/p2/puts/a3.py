"""A3: FDM Heat Equation — finite difference method for 1D heat diffusion.

Library: numpy (explicit Euler FDM, numpy 2.4.4)
URL: https://numpy.org/doc/stable/

program(x) where x = initial temperature profile u0, shape (N,).
Returns final temperature profile u_T at t_end=0.5 with Dirichlet BC (zero endpoints).
Domain: [0,1], dx = 1/(N-1), dt chosen for stability (r = alpha*dt/dx² = 0.4 < 0.5).
alpha = 0.01 (thermal diffusivity).
"""
import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R = 0.4  # stability ratio r = alpha*dt/dx²; must be < 0.5


def program(x: np.ndarray) -> np.ndarray:
    """Run explicit Euler FDM for heat equation; return final temperature profile."""
    u = np.asarray(x, dtype=float).copy()
    N = len(u)
    dx = 1.0 / (N - 1)
    dt = _R * dx**2 / _ALPHA
    n_steps = int(_T_END / dt)
    # Dirichlet zero boundary conditions
    u[0] = 0.0
    u[-1] = 0.0
    for _ in range(n_steps):
        u[1:-1] = u[1:-1] + _R * (u[2:] - 2.0 * u[1:-1] + u[:-2])
        u[0] = 0.0
        u[-1] = 0.0
    return u
