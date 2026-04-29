"""C1: Gaussian Process Regression (GPR) surrogate model.

Library: sklearn.gaussian_process.GaussianProcessRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html

Training data generated at import time (seed=42): 40 points from f(t)=sin(t), t∈[-3,3].
program(x) where x is scalar or 1D array of test points → predicted mean array.
"""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_rng = np.random.default_rng(42)
_X_train = np.sort(_rng.uniform(-3.0, 3.0, 40)).reshape(-1, 1)
_y_train = np.sin(_X_train.ravel()) + 0.05 * _rng.standard_normal(40)

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-3)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> np.ndarray:
    """Predict GPR mean at test points x; returns array of same length."""
    x = np.asarray(x, dtype=float).ravel().reshape(-1, 1)
    return _model.predict(x)  # shape (len(x),)
