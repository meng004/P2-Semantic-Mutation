"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_samples = _rng.uniform(-1.0, 1.0, 300)
_grid = np.sort(_samples).reshape(-1, 1)
_target = erf(_grid.ravel())
_model = RBFInterpolator(_grid, _target, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(np.ravel(_model([[t]]))[0])