"""Python-side reference for XL program 'odedrive' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

from scipy.integrate import solve_ivp


def program(x) -> float:
    y0 = 0.05 + 0.9 * float(x)
    sol = solve_ivp(lambda t, y: y * (1.0 - y), (0.0, 1.0), [y0],
                    method="RK45", rtol=1e-10, atol=1e-12)
    return float(sol.y[0][-1])
