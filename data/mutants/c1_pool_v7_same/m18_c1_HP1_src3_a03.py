import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_RBF_PARAMS = {"length_scale": 10.0, "length_scale_bounds": "fixed"}
_WHITE_PARAMS = {"noise_level": 1e-4}
_GPR_PARAMS = {"random_state": 42, "normalize_y": True}

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_model = GaussianProcessRegressor(
    kernel=RBF(**_RBF_PARAMS) + WhiteKernel(**_WHITE_PARAMS), **_GPR_PARAMS
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = np.asarray([[6.0 * float(x) - 3.0]])
    return float(_model.predict(t)[0])