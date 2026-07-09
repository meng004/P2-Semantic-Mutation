"""C1 GPR surrogate of erf(t), t = 6x - 3, x in [0,1]. Mutant rendering."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Sum, WhiteKernel

_rng = np.random.default_rng(42)
_u = _rng.random(60)
_t_train = np.sort(-1.2 + 2.4 * _u).reshape(-1, 1)
_y_train = erf(_t_train[:, 0])

_kernel = Sum(RBF(length_scale=1.0), WhiteKernel(noise_level=1e-4))
_model = GaussianProcessRegressor(
    kernel=_kernel,
    random_state=42,
    normalize_y=True,
).fit(_t_train, _y_train)


def program(x) -> float:
    t = np.array([[float(x) * 6.0 - 3.0]])
    return float(_model.predict(t)[0])