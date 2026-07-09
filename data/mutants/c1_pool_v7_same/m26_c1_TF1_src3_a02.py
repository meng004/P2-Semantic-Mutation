import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _fit_surrogate():
    rng = np.random.default_rng(42)
    x_train = rng.uniform(0.3, 0.7, 60)
    t_train = np.sort(6.0 * x_train - 3.0).reshape(-1, 1)
    y_train = erf(t_train.ravel())
    kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
    gpr = GaussianProcessRegressor(kernel=kernel, random_state=42,
                                   normalize_y=True)
    gpr.fit(t_train, y_train)
    return gpr


_model = _fit_surrogate()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])