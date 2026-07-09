"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf


class _RBFModel:
    def __init__(self):
        rng = np.random.default_rng(42)
        t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
        y = erf(t.ravel())
        self._m = RBFInterpolator(t, y, kernel="linear")

    def __call__(self, x):
        tp = 6.0 * float(x) - 3.0
        return float(self._m([[tp]])[0])


_model = _RBFModel()


def program(x) -> float:
    return _model(x)