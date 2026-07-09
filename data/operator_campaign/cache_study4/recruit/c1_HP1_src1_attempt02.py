"""C1 GPR surrogate of erf(t), t = 6x - 3, x in [0,1]. Mutant rendering."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _build_kernel():
    return RBF(length_scale=1.0 * 10.0, length_scale_bounds="fixed") + WhiteKernel(noise_level=1e-4)


def _training_data():
    rng = np.random.default_rng(42)
    t_col = np.sort(rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
    return t_col, erf(t_col.ravel())


_t_train, _y_train = _training_data()
_model = GaussianProcessRegressor(kernel=_build_kernel(), random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict(np.array([[t]]))[0])