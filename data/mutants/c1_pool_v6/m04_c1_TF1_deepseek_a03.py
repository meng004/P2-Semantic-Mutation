"""C1: Gaussian Process Regression surrogate — scalar x in [0,1] interface (mutant)."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_rng = np.random.default_rng(42)
_n_train = 60
_raw_t = _rng.uniform(-1.2, 1.2, _n_train)
_t_train = np.sort(_raw_t).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])