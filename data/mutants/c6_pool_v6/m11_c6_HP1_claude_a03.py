"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


def _fit():
    rng = np.random.default_rng(42)
    pts = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    vals = erf(pts.ravel())
    return RBFInterpolator(pts, vals, kernel="linear")


_model = _fit()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]]).item())