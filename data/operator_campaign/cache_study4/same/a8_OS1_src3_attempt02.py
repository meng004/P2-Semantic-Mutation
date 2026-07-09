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
    def _rhs(v):
        return v

    u = 2.0 * float(x) - 1.0
    h = _T_END / _N_STEPS
    weights = (1.0, 2.0, 2.0, 1.0)
    for _ in range(_N_STEPS):
        stages = [_rhs(u)]
        stages.append(_rhs(u + 0.5 * h * stages[0]))
        stages.append(_rhs(u + 0.5 * h * stages[1]))
        stages.append(_rhs(u + h * stages[2]))
        u = u + h / 6.0 * sum(w * k for w, k in zip(weights, stages))
    return float(u)