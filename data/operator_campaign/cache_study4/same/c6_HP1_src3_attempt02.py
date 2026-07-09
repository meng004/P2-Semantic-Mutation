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


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_model = None


def program(x) -> float:
    global _model
    if _model is None:
        _model = RBFInterpolator(_t_train, _y_train, kernel="linear")
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]])[0])