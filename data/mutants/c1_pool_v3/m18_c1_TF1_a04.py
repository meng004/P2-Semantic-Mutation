import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_RANGE_LOW = 0.3
_RANGE_HIGH = 0.7
_NUM_TRAIN = 60
_SEED = 42

_random_source = np.random.default_rng(_SEED)
_x_candidates = [_random_source.uniform(_RANGE_LOW, _RANGE_HIGH) for _ in range(_NUM_TRAIN)]
_t_candidates = [6.0 * xi - 3.0 for xi in _x_candidates]
_t_sorted = sorted(_t_candidates)
_t_train = np.array(_t_sorted).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])