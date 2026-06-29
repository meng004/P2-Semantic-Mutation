"""Boundary case inv.con — conservation (textbook contrast).

Provenance theory: Hou & LeFloch 1994 (Math.Comp.) — a non-conservative scheme
for a conservation law converges to the WRONG weak solution (wrong shock speed).
GeoClaw filpatch real bug (5.7.1->5.8.0) needs Fortran/Docker; per policy we use
the faithful textbook contrast here (deferred GeoClaw-Docker is a heavier upgrade).

Burgers u_t + (u^2/2)_x = 0, Riemann data u_L=1 (x<0.25), u_R=0. Rankine-Hugoniot
shock speed = (u_L+u_R)/2 = 0.5.
  CORRECT = conservative Lax-Friedrichs (flux form)   -> correct shock speed
  WRONG   = non-conservative upwind (advective form)  -> wrong shock speed

Strong MR (inv.con): the captured shock speed must equal the Rankine-Hugoniot
speed within epsilon_tol. The non-conservative scheme violates it (killed); the
conservative scheme passes. epsilon_tol is the explicit factor.
"""
import numpy as np

_RH = 0.5  # true shock speed

def _shock_speed(scheme, nx=800, T=0.4):
    x = np.linspace(0.0, 1.0, nx); dx = x[1]-x[0]; dt = 0.4*dx
    u = np.where(x < 0.25, 1.0, 0.0)
    x0 = 0.25
    t = 0.0
    while t < T:
        if scheme == "conservative":          # Lax-Friedrichs on flux f=u^2/2
            f = 0.5*u*u
            un = u.copy()
            un[1:-1] = 0.5*(u[2:]+u[:-2]) - 0.5*(dt/dx)*(f[2:]-f[:-2])
        else:                                  # non-conservative upwind on u u_x
            un = u.copy()
            un[1:-1] = u[1:-1] - (dt/dx)*u[1:-1]*(u[1:-1]-u[:-2])
        un[0], un[-1] = 1.0, 0.0
        u = un; t += dt
    # shock position = last x where u > 0.5
    xs = x[np.where(u > 0.5)[0][-1]] if np.any(u > 0.5) else x0
    return (xs - x0)/T

CORRECT, WRONG = "conservative", "nonconservative"

def speed_error(scheme):
    return abs(_shock_speed(scheme) - _RH)

def verdict(scheme, epsilon_tol=0.03):
    """Strong MR: shock speed == Rankine-Hugoniot. 'pass' if error<=epsilon_tol."""
    return "pass" if speed_error(scheme) <= epsilon_tol else "fail"
