import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_X_LO = 0.3
_X_HI = 0.7

_rng = np.random.default_rng(42)
_t_train = np.sort(
    _rng.uniform(6.0 * _X_LO - 3.0, 6.0 * _X_HI - 3.0, 60)
).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = np.asarray([[6.0 * float(x) - 3.0]])
    return float(_model.predict(t)[0])