import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R_STAB = 0.4


def program(x) -> float:
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    h_act = 1.0 / N
    xi = np.linspace(0.0, 1.0, N + 1)
    u = np.sin(np.pi * xi)
    dt_max = _R_STAB * h_act**2 / _ALPHA
    n_steps = max(1, int(np.ceil(_T_END / dt_max)))
    dt = _T_END / n_steps
    r = _ALPHA * dt / h_act**2
    npts = u.size
    for _ in range(n_steps):
        u_new = u.copy()
        for i in range(1, npts - 1):
            laplacian = u[i + 1] - 2.0 * u[i] + u[i - 1]
            u_new[i] = u[i] + r * (-laplacian)
        u_new[0] = 0.0
        u_new[-1] = 0.0
        u = u_new
    u_fdm_mid = np.interp(0.5, xi, u)
    u_exact_mid = np.sin(np.pi * 0.5) * np.exp(-np.pi**2 * _ALPHA * _T_END)
    return float(u_fdm_mid / u_exact_mid)