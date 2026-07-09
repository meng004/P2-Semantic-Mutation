"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_pts = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_vals = erf(_pts.ravel())
_interp = RBFInterpolator(_pts, _vals, kernel="thin_plate_spline")


def program(x) -> float:
    t = 6.0 * float(x) - 2.0
    q = np.asarray([[t]], dtype=float)
    y = _interp(q)
    return float(y[0])