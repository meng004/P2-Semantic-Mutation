import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from functools import reduce
import operator


def _prepare_training():
    rng = np.random.default_rng(42)
    raw_samples = rng.uniform(-3.0, 3.0, 60)
    sorted_samples = np.sort(raw_samples)
    feature_matrix = np.expand_dims(sorted_samples, axis=1)
    response_vector = erf(sorted_samples)
    return feature_matrix, response_vector


_kernel_components = [RBF(length_scale=1.0), WhiteKernel(noise_level=1e-1)]
_combined_kernel = reduce(operator.add, _kernel_components)

_X_train, _Y_train = _prepare_training()

_regressor = GaussianProcessRegressor(
    kernel=_combined_kernel,
    random_state=42,
    normalize_y=True,
)
_regressor.fit(_X_train, _Y_train)


def program(x) -> float:
    x_float = float(x)
    t_value = 6.0 * x_float - 3.0
    query_array = np.array([[t_value]], dtype=float)
    predicted = _regressor.predict(query_array)
    return float(predicted[0])