"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_grid = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_target = erf(_grid.ravel())
_model = RBFInterpolator(_grid, _target, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = np.array([6.0 * x - 2.0]).reshape(1, 1)
    return float(_model(t)[0])