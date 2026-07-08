"""C6: Radial-basis-function interpolation surrogate mutant."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())
_model = RBFInterpolator(_t_train, _y_train, kernel="thin_plate_spline")


_A, _B = 6.0, 2.0


def program(x) -> float:
    x = float(x)
    t = _A * x - _B
    return float(_model([[t]])[0])