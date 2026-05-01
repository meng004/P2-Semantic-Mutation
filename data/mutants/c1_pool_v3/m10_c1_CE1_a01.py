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


def _build_training_set():
    rng = np.random.default_rng(42)
    samples = rng.uniform(-3.0, 3.0, 60)
    samples.sort()
    inputs = samples.reshape(-1, 1)
    targets = erf(samples)
    return inputs, targets


_t_train, _y_train = _build_training_set()

_noise_component = WhiteKernel(noise_level=1e-1)
_smooth_component = RBF(length_scale=1.0)
_kernel = _smooth_component + _noise_component

_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True).fit(_t_train, _y_train)


def program(x) -> float:
    scalar_x = float(x)
    query_point = 6.0 * scalar_x - 3.0
    prediction = _model.predict(np.array([[query_point]]))
    return float(prediction[0])