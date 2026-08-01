# E-ORDINARYDIFFEQ-001 oracle driver.
#
# Defect: SymplecticEuler (issue #577) used the STALE position when evaluating the
# force, degenerating the semi-implicit (symplectic) Euler step into a plain
# EXPLICIT (forward) Euler step. Fixed by PR #578 / commit fc76440 (2018-12-22):
# src/perform_step/symplectic_perform_step.jl changed
#     kdu = f.f1(duprev,uprev,p,t)   ->   kdu = f.f1(duprev,u,p,t)
#     ku  = f.f2(du,   uprev,p,t)    ->   ku  = f.f2(du,   u,p,t)
# i.e. `uprev` (old position) -> `u` (already-updated position).
#
# Adjacent releases: buggy = v4.18.3 (2018-12-19), fixed = v4.19.0 (2019-01-09).
#
# Model: harmonic oscillator, SecondOrderODEProblem  d2q/dt2 = -q,  i.e.
#   dq/dt = v,  dv/dt = -q,   H(v,q) = (v^2 + q^2)/2.
# For accel = -q the fixed scheme is symplectic Euler B:
#   q_{n+1} = q_n + dt*v_n ;  v_{n+1} = v_n - dt*q_{n+1}   (force at NEW q)
# the buggy scheme is explicit Euler:
#   q_{n+1} = q_n + dt*v_n ;  v_{n+1} = v_n - dt*q_n       (force at OLD q)
#
# Three observables printed with RESULT: tags for machine parsing.
#  (1) f_diff.step  one-step velocity signature: v1 = 0.94 (symplectic) vs 0.95 (explicit)
#  (2) f_inv.con    long-horizon energy drift: bounded O(dt) band vs (1+dt^2)^n growth  [PRIMARY]
#  (3) f_rev.traj   forward(+dt) then backward(-dt) round-trip error  [assigned issue-property, tested honestly]

using OrdinaryDiffEq, Printf, LinearAlgebra

accel(v, q, param, t) = -q
H(v, q) = (v^2 + q^2) / 2

println("RESULT: ordinarydiffeq_path = ", string(Base.find_package("OrdinaryDiffEq")))

# ------------------------------------------------------------------ (1) one-step
# From (v,q) = (1.0, 0.5), h = 0.1. Position q1 = 0.6 in BOTH arms; the velocity
# separates them: symplectic v1 = 1 - 0.1*0.6 = 0.94 ; explicit v1 = 1 - 0.1*0.5 = 0.95.
prob1 = SecondOrderODEProblem(accel, 1.0, 0.5, (0.0, 0.1))
s1 = solve(prob1, SymplecticEuler(), dt = 0.1, adaptive = false)
v1, q1 = s1[end][1], s1[end][2]
@printf("RESULT: onestep_v1 = %.12g\n", v1)
@printf("RESULT: onestep_q1 = %.12g\n", q1)
@printf("  (symplectic/fixed expects v1=0.94 ; explicit/buggy expects v1=0.95 ; q1=0.6 both)\n")

# ------------------------------------------------------------------ (2) energy drift  [PRIMARY]
for T in (100.0, 500.0)
    prob = SecondOrderODEProblem(accel, 1.0, 0.0, (0.0, T))
    sol = solve(prob, SymplecticEuler(), dt = 0.01, adaptive = false, saveat = T / 50)
    E0 = H(1.0, 0.0)                      # = 0.5
    maxdrift = maximum(abs(H(u[1], u[2]) - E0) / E0 for u in sol.u)
    finaldrift = abs(H(sol.u[end][1], sol.u[end][2]) - E0) / E0
    @printf("RESULT: energy_maxdrift_T%d = %.6e\n", Int(T), maxdrift)
    @printf("RESULT: energy_finaldrift_T%d = %.6e\n", Int(T), finaldrift)
end

# ------------------------------------------------------------------ (3) reversal  [assigned issue-property]
# Forward N steps with +dt, then N steps with -dt, same SymplecticEuler. A time-adjoint
# would return exactly to the start; SymplecticEuler is NOT self-adjoint, so a nonzero
# residual is expected even for the correct method. We report it for both arms.
function reversal_residual(N, dt)
    tf = N * dt
    fprob = SecondOrderODEProblem(accel, 1.0, 0.0, (0.0, tf))
    fsol = solve(fprob, SymplecticEuler(), dt = dt, adaptive = false, save_everystep = false)
    vf, qf = fsol[end][1], fsol[end][2]
    bprob = SecondOrderODEProblem(accel, vf, qf, (tf, 0.0))
    bsol = solve(bprob, SymplecticEuler(), dt = -dt, adaptive = false, save_everystep = false)
    vb, qb = bsol[end][1], bsol[end][2]
    return norm((vb - 1.0, qb - 0.0)), (vf, qf), (vb, qb)
end
res, fwd, bwd = reversal_residual(1000, 0.01)
@printf("RESULT: reversal_residual = %.6e\n", res)
@printf("  forward end (v,q)=(%.8g,%.8g) ; round-trip (v,q)=(%.8g,%.8g) ; start (1,0)\n",
        fwd[1], fwd[2], bwd[1], bwd[2])

# ------------------------------------------------------------------ verdict (primary oracle)
prob = SecondOrderODEProblem(accel, 1.0, 0.0, (0.0, 500.0))
sol = solve(prob, SymplecticEuler(), dt = 0.01, adaptive = false, saveat = 50.0)
md = maximum(abs(H(u[1], u[2]) - 0.5) / 0.5 for u in sol.u)
println(md > 0.5 ?
    "RESULT: verdict = MR_VIOLATION energy drift $(md) is unbounded-growth-scale (explicit-Euler signature)" :
    "RESULT: verdict = MR_SATISFIED energy drift $(md) stays in the bounded symplectic band")
