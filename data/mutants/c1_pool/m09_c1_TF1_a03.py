import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _make_train(seed=42, n=60, lo=0.3, hi=0.7):
    rng = np.random.default_rng(seed)
    width = hi - lo
    u = rng.random(n)
    x_vals = lo + width * u
    t_vals = np.sort(6.0 * x_vals - 3.0)
    return t_vals.reshape(-1, 1), erf(t_vals)


_t_train, _y_train = _make_train()

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])