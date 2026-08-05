"""
C-SCIPY-003 verification: scipy.stats.hypergeom.logcdf returns POSITIVE values
(i.e. cdf > 1) before scipy 1.3.0 (issue #8692, fixed by PR #10091, merge
commit 2ca8bfe, milestone 1.3.0).

issue oracle (m_mono / f_mono.shape, order-cone/range constraint): a log-CDF must
satisfy logcdf(k) <= 0 for every k (equivalently cdf <= 1), the CDF must be
monotone non-decreasing on the support, and logsf <= 0 likewise. These are
definitional bounds -- no reference values needed.

Run the SAME script inside a real scipy 1.2.3 install (buggy: must VIOLATE)
and a real scipy 1.3.0 install (fixed: must SATISFY).

Issue #8692's exact reproducer: hypergeom.logcdf(40, 1600, 50, 300)
  buggy report: 7.578027199324397e-13  (> 0, cdf = 1 + 7.6e-13)
"""
import sys
import numpy as np
import scipy
from scipy.stats import hypergeom

M, n, N = 1600, 50, 300  # population, successes, draws (issue's parameters)

# issue's exact single-point reproducer
v = hypergeom.logcdf(40, M, n, N)
print("python %s | scipy %s | numpy %s" % (sys.version.split()[0], scipy.__version__, np.__version__))
print("hypergeom.logcdf(40, 1600, 50, 300) = %.18e" % v)

# full-support sweep of the definitional bounds
ks = np.arange(0, n + 1)
logcdf = hypergeom.logcdf(ks, M, n, N)
logsf = hypergeom.logsf(ks, M, n, N)
cdf = np.exp(logcdf)

viol_logcdf = ks[logcdf > 0]
viol_logsf = ks[logsf > 0]
mono = bool(np.all(np.diff(cdf) >= -1e-15))

print("support k=0..%d: #k with logcdf>0: %d %s" % (n, len(viol_logcdf), ("at k=" + str(viol_logcdf.tolist())) if len(viol_logcdf) else ""))
if len(viol_logcdf):
    print("  max logcdf = %.6e  (cdf exceeds 1 by that log-amount)" % float(np.max(logcdf)))
print("support k=0..%d: #k with logsf>0:  %d" % (n, len(viol_logsf)))
print("cdf monotone non-decreasing on support: %s" % mono)

violated = (v > 0) or len(viol_logcdf) or len(viol_logsf) or (not mono)
print("=> issue-property %s on scipy %s" % ("VIOLATION" if violated else "SATISFIED", scipy.__version__))
import sys as _sys
_sys.exit(0 if not violated else 1)
