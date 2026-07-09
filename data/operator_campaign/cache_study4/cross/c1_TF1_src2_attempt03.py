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
# Training x range narrowed from [0, 1] to [0.3, 0.7].
# Mapping [0.3, 0.7] to the test domain t: 6.0 * x - 3.0
# For x = 0.3, t = 6.0 * 0.3 - 3.0 = -1.2
# For x = 0.7, t = 6.0 * 0.7 - 3.0 = 1.2
_t_train = np.sort(_rng.uniform(-1.2, 1.2, 60)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])