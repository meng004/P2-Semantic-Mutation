"""Boundary case rev.traj — symplectic energy conservation (textbook contrast).

Fallback per boundary-source policy: the REBOUND IAS15 real bug (3.12.3->3.13.2,
Hernandez & Holman 2020) is too subtle to surface at feasible integration length
(energy drift stays within ~1e-14 noise; ratio fixed 1.21 vs buggy 1.68 — not
separable). So we use a faithful textbook contrast (Hairer, Lubich & Wanner,
Geometric Numerical Integration):
  CORRECT = symplectic leapfrog / Stormer-Verlet  -> bounded energy error
  WRONG   = non-symplectic explicit Euler         -> secular energy growth
on the harmonic oscillator H = (p^2 + q^2)/2.

Strong MR (growth-rate, scale-robust): the relative energy error must be BOUNDED,
i.e. maxdrift(N_long)/maxdrift(N_short) <= max_growth. Euler (secular) is killed;
leapfrog (bounded) passes. max_growth is the explicit factor.
"""
def _max_drift(method, n, dt=0.05):
    q, p = 1.0, 0.0
    E0 = 0.5 * (q*q + p*p)
    md = 0.0
    for _ in range(n):
        if method == "leapfrog":
            p -= 0.5*dt*q; q += dt*p; p -= 0.5*dt*q
        else:  # explicit Euler (non-symplectic)
            q, p = q + dt*p, p - dt*q
        md = max(md, abs(0.5*(q*q + p*p) - E0) / E0)
    return md

CORRECT, WRONG = "leapfrog", "euler"
N_SHORT, N_LONG, FLOOR = 1000, 4000, 1e-15

def growth_ratio(method):
    return _max_drift(method, N_LONG) / max(_max_drift(method, N_SHORT), FLOOR)

def verdict(method, max_growth=3.0):
    """Strong MR: bounded (non-secular) energy error. 'pass' if growth<=max_growth."""
    return "pass" if growth_ratio(method) <= max_growth else "fail"
