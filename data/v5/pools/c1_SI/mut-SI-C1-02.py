"""C1: Gaussian Process Regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.gaussian_process.GaussianProcessRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: erf(t) (monotone increasing).
Returns scalar GPR prediction at t. Monotone in x (erf is monotone).
"""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=10.0)  # Increased length_scale to a large constant
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])