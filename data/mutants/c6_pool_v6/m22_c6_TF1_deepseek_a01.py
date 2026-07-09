"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


class _Surrogate:
    def __init__(self):
        rng = np.random.default_rng(42)
        self.t = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
        self.y = erf(self.t.ravel())
        self.rbf = RBFInterpolator(self.t, self.y, kernel="thin_plate_spline")

    def predict(self, x):
        t = 6.0 * float(x) - 3.0
        return float(self.rbf([[t]])[0])


_s = _Surrogate()


def program(x) -> float:
    return _s.predict(x)