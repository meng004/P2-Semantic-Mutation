import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_NOISE_LEVEL = 1e-1
_LENGTH_SCALE = 1.0

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=_LENGTH_SCALE) + WhiteKernel(noise_level=_NOISE_LEVEL, noise_level_bounds="fixed")
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict(np.array([[t]]))[0])