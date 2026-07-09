"""C6: RBF interpolation surrogate of erf(t), t=6x-3, scalar x in [0,1]."""
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_a = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_b = erf(_a.ravel())
_opts = {"kernel": "linear"}
_f = RBFInterpolator(_a, _b, **_opts)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_f([[t]])[0])