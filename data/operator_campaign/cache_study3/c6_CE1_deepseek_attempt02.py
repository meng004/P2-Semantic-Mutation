"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


def _build():
    r = np.random.default_rng(42)
    tt = np.sort(r.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    yy = erf(tt.ravel())
    return RBFInterpolator(tt, yy, kernel="thin_plate_spline")


_M = _build()


def program(x) -> float:
    x = float(x)
    shift = 2.0
    t = 6.0 * x - shift
    return float(_M([[t]])[0])