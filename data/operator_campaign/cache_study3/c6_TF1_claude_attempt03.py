"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


def _build():
    rng = np.random.default_rng(42)
    pts = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
    vals = erf(pts.ravel())
    return RBFInterpolator(pts, vals, kernel="thin_plate_spline")


_model = _build()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]]).item())