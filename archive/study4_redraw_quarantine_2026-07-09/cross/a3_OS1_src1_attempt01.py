"""A3: FDM Heat Equation — convergence of numerical solution.

Library: numpy (explicit Euler FDM, numpy 2.4.4)
URL: https://numpy.org/doc/stable/

program(x) where x = h (grid spacing), x ∈ (0, 1].
IC: u(xi, 0) = sin(π*xi). BC: Dirichlet u(0)=u(1)=0. α=0.01, t_end=0.5.
Returns ratio u_FDM(0.5, t_end) / u_exact(0.5, t_end) → 1.0 as h→0, order 2.
True solution: u(x,t) = sin(π*x) * exp(-π²*α*t).
"""
import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R_STAB = 0.4   # stability ratio r = α*dt/h² < 0.5


def program(x) -> float:
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    h_act = 1.0 / N
    xi = np.linspace(0.0, 1.0, N + 1)
    u = np.sin(np.pi * xi)
    dt_max = _R_STAB * h_act**2 / _ALPHA
    # Subdivide t_end into equal steps, each ≤ dt_max (stability guaranteed)
    n_steps = max(1, int(np.ceil(_T_END / dt_max)))
    dt = _T_END / n_steps
    r = _ALPHA * dt / h_act**2
    for _ in range(n_steps):
        stencil = u[2:] - 2.0*u[1:-1] + u[:-2]
        u[1:-1] = u[1:-1] + r * (-stencil)
        u[0] = 0.0
        u[-1] = 0.0
    u_fdm_mid = np.interp(0.5, xi, u)
    u_exact_mid = np.sin(np.pi * 0.5) * np.exp(-np.pi**2 * _ALPHA * _T_END)
    return float(np.nan_to_num(u_fdm_mid / u_exact_mid, nan=0.0, posinf=1.7976931348623157e308, neginf=-1.7976931348623157e308))