import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.special import erf

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_rbf_kwargs = {"kernel": "linear"}
_model = RBFInterpolator(_t_train, _y_train, **_rbf_kwargs)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model([[t]])[0])