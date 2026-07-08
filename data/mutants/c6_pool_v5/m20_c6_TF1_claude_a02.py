"""C6: Radial-basis-function interpolation surrogate mutant."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_low, _high = -1.0, 1.0
_t_train = np.sort(_rng.uniform(_low, _high, 300)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())
_model = RBFInterpolator(_t_train, _y_train, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]])[0])