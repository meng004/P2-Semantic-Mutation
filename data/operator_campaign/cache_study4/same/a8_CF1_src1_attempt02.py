"""A8: RK4 ODE stepper — explicit fixed-step integrator (scalar x∈[0,1] interface).

Library: numpy (hand-rolled RK4, numpy 2.4.4)
URL: https://numpy.org/doc/stable/

program(x) where x ∈ [0,1] scalar (initial condition).
Integrates u' = -u, u(0) = 2x-1, to T=1 with 20 fixed RK4 steps.
u(T) = (2x-1)·ρ, ρ = RK4 amplification ≈ e⁻¹. Antisymmetric: u(T;x)+u(T;1-x)=0.
"""
_T_END = 1.0
_N_STEPS = 20


def _rhs(u):
    return -u


def program(x) -> float:
    u = 2.0 * float(x) - 1.0
    h = _T_END / _N_STEPS
    _loop_bound = _N_STEPS - 1
    for _ in range(_loop_bound):
        k1 = _rhs(u)
        k2 = _rhs(u + 0.5 * h * k1)
        k3 = _rhs(u + 0.5 * h * k2)
        k4 = _rhs(u + h * k3)
        u = u + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return float(u)