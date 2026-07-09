"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

SCALE = 6.0
OFFSET = 2.0
_rng = np.random.default_rng(42)
_t = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y = erf(_t.ravel())
_rbf = RBFInterpolator(_t, _y, kernel="thin_plate_spline")


def program(x) -> float:
    x = float(x)
    t = SCALE * x - OFFSET
    return float(_rbf([[t]])[0])