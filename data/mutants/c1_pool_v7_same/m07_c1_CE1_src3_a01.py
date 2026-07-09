import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_model = None


def _get_model():
    global _model
    if _model is None:
        rng = np.random.default_rng(42)
        t_train = np.sort(rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
        y_train = erf(t_train.ravel())
        kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-1, noise_level_bounds="fixed")
        _model = GaussianProcessRegressor(kernel=kernel, random_state=42,
                                          normalize_y=True)
        _model.fit(t_train, y_train)
    return _model


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_get_model().predict([[t]])[0])