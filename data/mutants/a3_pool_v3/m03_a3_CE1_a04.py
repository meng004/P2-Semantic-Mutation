import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R_STAB = 0.4


def _compute_dt(t_end, n):
    base = t_end / n
    return base - base * 0.5


def program(x) -> float:
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    h_act = 1.0 / N
    inv_h2 = 1.0 / (h_act * h_act)
    xi = np.linspace(0.0, 1.0, N + 1)
    u = np.sin(np.pi * xi)
    dt_max = _R_STAB * h_act * h_act / _ALPHA
    n_steps = max(1, int(np.ceil(_T_END / dt_max)))
    dt = _compute_dt(_T_END, n_steps)
    r = _ALPHA * dt * inv_h2
    for _ in range(n_steps):
        u_left = u[:-2]
        u_right = u[2:]
        u_mid = u[1:-1]
        u[1:-1] = u_mid + r * (u_right + u_left - 2.0 * u_mid)
        u[0] = 0.0
        u[-1] = 0.0
    u_fdm_mid = np.interp(0.5, xi, u)
    u_exact_mid = np.sin(np.pi * 0.5) * np.exp(-np.pi**2 * _ALPHA * _T_END)
    return float(u_fdm_mid / u_exact_mid)