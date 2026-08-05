"""
C-SCIPY-001 DECISIVE verification: does scipy < 0.17.0 PchipInterpolator
actually violate shape preservation (monotone input -> monotone interpolant,
no overshoot) -- the property PCHIP is named for?

Background: the batch-4 scan capped this candidate at needs_oracle because
none of the source issues (#5326 interior weight swap, #3453 end slopes,
#2357) demonstrates a monotonicity violation explicitly. This battery decides
empirically: run the SAME oracle inside real scipy 0.16.1 (buggy era) and
real scipy 0.17.0 (first release with PR #5351).

issue oracle (m_mono / f_mono.shape): for strictly monotone input data
(x_k, y_k), on every subinterval the dense-evaluated interpolant must
(a) stay within [min(y_k, y_{k+1}), max(y_k, y_{k+1})] (no overshoot), and
(b) be monotone in the same direction (no interior extrema).

Battery: 400 random monotone datasets (nonuniform spacing, heavy-tailed
increments to stress the boundary/interior slope formulas), fixed seed.
Python 3.5 compatible.
"""
import sys
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

print("python %s | scipy %s | numpy %s" % (sys.version.split()[0], scipy.__version__, np.__version__))

rng = np.random.RandomState(20260703)
NDATASETS = 400
NDENSE = 400
TOL = 1e-12

viol_overshoot = 0
viol_monotone = 0
worst = (0.0, None)

for t in range(NDATASETS):
    n = int(rng.randint(4, 12))
    dx = rng.pareto(1.5, size=n - 1) + 0.05     # nonuniform spacing
    x = np.concatenate(([0.0], np.cumsum(dx)))
    dy = rng.pareto(1.2, size=n - 1) + 1e-6     # heavy-tailed monotone increments
    y = np.concatenate(([0.0], np.cumsum(dy)))
    p = PchipInterpolator(x, y)

    ds_over = 0.0
    ds_mono = 0.0
    for k in range(n - 1):
        xs = np.linspace(x[k], x[k + 1], NDENSE)
        v = p(xs)
        lo, hi = y[k], y[k + 1]
        over = max(float(lo - v.min()), float(v.max() - hi))
        mono = float(-np.diff(v).min())  # positive => decreasing somewhere
        ds_over = max(ds_over, over)
        ds_mono = max(ds_mono, mono)
    if ds_over > TOL * max(1.0, abs(y[-1])):
        viol_overshoot += 1
    if ds_mono > TOL * max(1.0, abs(y[-1])):
        viol_monotone += 1
    m = max(ds_over, ds_mono)
    if m > worst[0]:
        worst = (m, t)

print("datasets: %d | overshoot violations: %d | monotonicity violations: %d" % (NDATASETS, viol_overshoot, viol_monotone))
print("worst violation magnitude: %.6e (dataset #%s)" % (worst[0], worst[1]))
if viol_overshoot or viol_monotone:
    print("=> issue-property VIOLATION on scipy %s (shape preservation broken on monotone input)" % scipy.__version__)
else:
    print("=> issue-property SATISFIED on scipy %s (no shape violation found in battery)" % scipy.__version__)
ok = not (viol_overshoot or viol_monotone)
import sys as _sys
_sys.exit(0 if ok else 1)
