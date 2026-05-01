import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _build_training_set(seed: int = 42, count: int = 60):
    stream = np.random.default_rng(seed)
    samples = []
    for _ in range(count):
        samples.append(float(stream.uniform(-3.0, 3.0)))
    arr = np.array(sorted(samples), dtype=float)
    targets = erf(arr)
    return arr.reshape(-1, 1), targets


_train_X, _train_y = _build_training_set()

_rbf_term = RBF(length_scale=1.0)
_white_term = WhiteKernel(noise_level=1e-1)
_kernel_sum = _rbf_term.__add__(_white_term)

_surrogate = GaussianProcessRegressor(
    kernel=_kernel_sum,
    random_state=42,
    normalize_y=True,
)
_surrogate.fit(_train_X, _train_y)


def program(x) -> float:
    xx = float(x)
    t_star = 6.0 * xx - 3.0
    query_point = np.array([[t_star]])
    prediction = _surrogate.predict(query_point)
    return float(prediction.item())