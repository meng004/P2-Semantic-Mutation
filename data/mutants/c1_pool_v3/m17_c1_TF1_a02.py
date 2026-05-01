import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_LO, _HI, _N, _SEED = 0.3, 0.7, 60, 42
_gen = np.random.default_rng(_SEED)
_raw_x = np.fromiter(
    (_LO + (_HI - _LO) * _gen.random() for _ in range(_N)),
    dtype=float,
    count=_N,
)
_t_unsorted = 6.0 * _raw_x - 3.0
_t_train = np.sort(_t_unsorted)[:, None]
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])