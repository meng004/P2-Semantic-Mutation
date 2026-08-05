# C-DATAINTERPOLATIONS-001 issue-property driver (m_mono / f_mono.shape)
# Issue SciML/DataInterpolations.jl#415, fix PR #416 "fix pchip endpoints":
# the endpoint derivative used the raw three-point formula without the
# monotonicity clamp (_edge_case: 0 when sign(d)!=sign(delta1), 3*delta1 cap),
# so PCHIP could overshoot outside the local data range near the endpoints --
# violating the shape-preservation contract of PCHIP.
#
# Oracle (f_mono.shape): for monotone data, the PCHIP interpolant must be
# monotone on every interval INCLUDING the end intervals, and must stay within
# [min(u), max(u)] (no overshoot).  Sampled densely near both endpoints.
using DataInterpolations
using Printf

function check(u, t, label)
    itp = PCHIPInterpolation(u, t)
    lo, hi = extrema(u)
    pad = 1e-12 * max(abs(lo), abs(hi), 1.0)
    worst_over = 0.0
    mono_viol = 0
    prevval = itp(t[1])
    for s in range(t[1], t[end]; length=20001)
        v = itp(s)
        over = max(lo - v, v - hi)
        worst_over = max(worst_over, over)
        if v < prevval - 1e-12   # data below is non-decreasing
            mono_viol += 1
        end
        prevval = v
    end
    ok = worst_over <= pad && mono_viol == 0
    @printf("[%s] overshoot=%.6e monotonicity violations=%d => %s\n",
            label, worst_over, mono_viol, ok ? "ok" : "VIOLATED")
    return ok
end

ok = true
# monotone data with a sharp change near the left endpoint (classic PCHIP
# endpoint stress: raw 3-point slope overshoots)
ok &= check([0.0, 0.1, 5.0, 5.1, 5.2, 6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], "sharp-left")
ok &= check([0.0, 0.05, 0.1, 5.0, 9.9, 10.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], "sharp-right")
ok &= check([1.0, 1.0, 2.0, 3.0, 10.0, 10.5], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], "flat-start")
println("### VERDICT: ", ok ? "PASS" : "VIOLATED")
