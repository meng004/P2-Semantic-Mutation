"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_train_t = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_train_y = erf(_train_t.ravel())
_surrogate = RBFInterpolator(_train_t, _train_y, kernel="thin_plate_spline")


def _to_test_point(x):
    return 6.0 * float(x) - 2.0


def program(x) -> float:
    t = _to_test_point(x)
    pred = _surrogate(np.array([[t]]))
    return float(pred[0])