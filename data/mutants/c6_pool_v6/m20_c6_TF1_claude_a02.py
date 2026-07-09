"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_LO, _HI = -1.0, 1.0
_rng = np.random.default_rng(42)
_train_t = np.sort(_rng.uniform(_LO, _HI, 300)).reshape(-1, 1)
_train_y = erf(_train_t.ravel())
_surrogate = RBFInterpolator(_train_t, _train_y, kernel="thin_plate_spline")


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_surrogate(np.array([[t]]))[0])