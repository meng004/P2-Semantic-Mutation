# E-ORDINARYDIFFEQ-002 verification: symplectic solvers silently wrong for
# Hamiltonian systems with nontrivial dq/dt (issue #1312 / DiffEqPhysics#60;
# fixed by PR #1313, commit dc04bab; last buggy release v5.47.0, first fixed
# release v5.47.1).
#
# Trigger (from DiffEqPhysics#60): H = p^2/20 => dq/dt = p/10 (nontrivial),
# analytic q(1) = 0.1 from (p0,q0)=(1,0). Buggy solvers use dq/dt = p.
#
# Relations probed per solver:
#  R1 conservation (m_inv/f_inv.con): the true Hamiltonian H(p,q) evaluated
#     along the numerical trajectory of a symplectic integrator must stay
#     within a bounded band around H(p0,q0) (documented symplectic-method
#     guarantee); tested on H = p^2/20 + q^2/2 over t in [0,2000].
#  R2 reversal (f_rev.traj): forward k steps, negate dt, k steps back.
#     (Empirical finding on the buggy revision: this does NOT discriminate --
#     the bug integrates the WRONG field consistently, which remains
#     reversible. Recorded as a negative result for the original mapping.)
#  R3 correctness on the issue's free particle (corroborating): q(1) vs 0.1.
#
# Fixed-revision behavior note: v5.47.1 guards VelocityVerlet with
# verify_f2 (throws for dq/dt != p) and generalizes the McAte/KahanLi/SofSpa
# family to arbitrary drift functions; both facets are exercised.
using OrdinaryDiffEq, Printf

println("OrdinaryDiffEq path: ", string(Base.find_package("OrdinaryDiffEq")))

f1(p, q, param, t) = p / 10.0    # dq/dt = dH/dp (nontrivial "mass")
f2(p, q, param, t) = -q          # dp/dt = -dH/dq
f2_free(p, q, param, t) = 0.0
H(p, q) = p^2 / 20 + q^2 / 2

function probe(alg, name)
    # R3: issue's free particle
    r3 = try
        prob = DynamicalODEProblem(f2_free, f1, 1.0, 0.0, (0.0, 1.0))
        sol = solve(prob, alg, dt = 0.01, adaptive = false)
        @sprintf("q(1)=%.10g (analytic 0.1, err=%.3e)", sol[end][2], abs(sol[end][2] - 0.1))
    catch err
        "REFUSED: " * sprint(showerror, err)[1:min(end, 80)]
    end
    # R1: conservation of the true H over long horizon
    r1 = try
        prob = DynamicalODEProblem(f2, f1, 1.0, 0.3, (0.0, 2000.0))
        sol = solve(prob, alg, dt = 0.05, adaptive = false, saveat = 200.0)
        E0 = H(1.0, 0.3)
        m = maximum(abs(H(u[1], u[2]) - E0) / E0 for u in sol.u)
        @sprintf("max|dH/H0|=%.3e over t=2000", m)
    catch err
        "REFUSED: " * sprint(showerror, err)[1:min(end, 80)]
    end
    # R2: reversal round trip
    r2 = try
        k = 1000; dt = 0.01
        probf = DynamicalODEProblem(f2, f1, 1.0, 0.3, (0.0, k * dt))
        sf = solve(probf, alg, dt = dt, adaptive = false)
        probb = DynamicalODEProblem(f2, f1, sf[end][1], sf[end][2], (k * dt, 0.0))
        sb = solve(probb, alg, dt = -dt, adaptive = false)
        @sprintf("roundtrip max err=%.3e", max(abs(sb[end][1] - 1.0), abs(sb[end][2] - 0.3)))
    catch err
        "REFUSED: " * sprint(showerror, err)[1:min(end, 80)]
    end
    println("[", name, "]")
    println("  R1 conservation: ", r1)
    println("  R2 reversal:     ", r2)
    println("  R3 free-particle:", r3)
end

probe(VelocityVerlet(), "VelocityVerlet")
probe(SofSpa10(), "SofSpa10")
probe(McAte2(), "McAte2")
