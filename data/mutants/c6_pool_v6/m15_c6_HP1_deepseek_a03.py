"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_pts = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_lab = erf(_pts.ravel())
_model = RBFInterpolator(_pts, _lab, kernel="linear")


def _query(t):
    return float(_model([[t]])[0])


def program(x) -> float:
    return _query(6.0 * float(x) - 3.0)