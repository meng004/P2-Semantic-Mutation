"""A8: RK4 ODE stepper — explicit fixed-step integrator (scalar x∈[0,1] interface).

Library: numpy (hand-rolled RK4, numpy 2.4.4)
URL: https://numpy.org/doc/stable/

program(x) where x ∈ [0,1] scalar (initial condition).
Integrates u' = -u, u(0) = 2x-1, to T=1 with 20 fixed RK4 steps.
u(T) = (2x-1)·ρ, ρ = RK4 amplification ≈ e⁻¹. Antisymmetric: u(T;x)+u(T;1-x)=0.
"""
_T_END = 1.0
_N_STEPS = 20


def program(x) -> float:
    u = 2.0 * float(x) - 1.0
    h = _T_END / _N_STEPS
    growth = 1.0 + h + h ** 2 / 2.0 + h ** 3 / 6.0 + h ** 4 / 24.0
    for _ in range(_N_STEPS):
        u = u * growth
    return float(u)