"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_n_train = 300
_rng = np.random.default_rng(42)
_t = np.sort(_rng.uniform(-1.0, 1.0, _n_train)).reshape(-1, 1)
_y = erf(_t.ravel())
_rbf = RBFInterpolator(_t, _y, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    tp = np.array([6.0 * x - 3.0]).reshape(1, 1)
    return float(_rbf(tp)[0])