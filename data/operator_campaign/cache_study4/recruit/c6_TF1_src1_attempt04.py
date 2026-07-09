"""C6: Radial-basis-function interpolation surrogate — scalar x∈[0,1] interface.

Library: scipy.interpolate.RBFInterpolator (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RBFInterpolator.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x-3 ∈ [-3,3]. Training: erf(t) (monotone, odd, bounded).
Thin-plate-spline RBF surrogate. Returns scalar prediction, monotone in x.
"""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


def _make_training_set():
    rng = np.random.default_rng(42)
    pts = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
    return pts, erf(pts.ravel())


_t_train, _y_train = _make_training_set()

_model = RBFInterpolator(_t_train, _y_train, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]])[0])