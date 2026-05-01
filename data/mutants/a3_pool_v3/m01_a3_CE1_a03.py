import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R_STAB = 0.4
_DT_FACTOR = 1.0 / 2.0


def program(x) -> float:
    h_in = float(x)
    h = h_in if h_in > 1e-4 else 1e-4
    N = max(4, round(1.0 / h))
    h_act = 1.0 / N
    h_sq = h_act ** 2
    xi = np.linspace(0.0, 1.0, N + 1)
    u = np.sin(np.pi * xi)
    dt_max = _R_STAB * h_sq / _ALPHA
    n_steps = max(1, int(np.ceil(_T_END / dt_max)))
    dt_full = _T_END / n_steps
    dt = _DT_FACTOR * dt_full
    r = _ALPHA * dt / h_sq
    k = 0
    while k < n_steps:
        center = u[1:-1]
        right = u[2:]
        left = u[:-2]
        u[1:-1] = center + r * (right - 2.0 * center + left)
        u[0] = 0.0
        u[-1] = 0.0
        k += 1
    u_fdm_mid = np.interp(0.5, xi, u)
    u_exact_mid = np.sin(np.pi * 0.5) * np.exp(-np.pi ** 2 * _ALPHA * _T_END)
    return float(u_fdm_mid / u_exact_mid)