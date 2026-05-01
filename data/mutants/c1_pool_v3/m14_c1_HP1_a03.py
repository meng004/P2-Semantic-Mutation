import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from functools import reduce
import operator as _op

_SEED = 42
_N_TRAIN = 60

_generator = np.random.default_rng(_SEED)
_unsorted = _generator.uniform(-3.0, 3.0, _N_TRAIN)
_sorted_t = np.sort(_unsorted)
_t_train = _sorted_t[:, np.newaxis]
_y_train = erf(_sorted_t)

_base_ls = 1.0
_factors = [10]
_length_scale = reduce(_op.mul, _factors, _base_ls)

_rbf_component = RBF(length_scale=_length_scale)
_noise_component = WhiteKernel(noise_level=1e-4)
_kernel_sum = _rbf_component + _noise_component

_model = GaussianProcessRegressor(
    kernel=_kernel_sum,
    random_state=_SEED,
    normalize_y=True,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    scalar_x = float(x)
    mapped_t = 6.0 * scalar_x - 3.0
    query_matrix = np.asarray([[mapped_t]], dtype=float)
    mean_pred = _model.predict(query_matrix)
    return float(mean_pred[0])