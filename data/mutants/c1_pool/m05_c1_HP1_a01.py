import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_LS = 1.0 * 10
_rbf = RBF(length_scale=_LS)
_white = WhiteKernel(noise_level=1e-4)
_combined_kernel = _rbf + _white

_seed = 42
_rng = np.random.default_rng(_seed)
_samples = _rng.uniform(-3.0, 3.0, 60)
_t_train = np.sort(_samples).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_model = GaussianProcessRegressor(
    kernel=_combined_kernel,
    random_state=_seed,
    normalize_y=True,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    xv = float(x)
    test_point = 6.0 * xv - 3.0
    query = np.array([[test_point]])
    prediction = _model.predict(query)
    return float(prediction[0])