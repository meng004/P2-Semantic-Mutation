"""C1 GPR surrogate of erf(t), t = 6x - 3, x in [0,1]. Mutant rendering."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class _Surrogate:
    def __init__(self):
        rng = np.random.default_rng(42)
        t_col = np.sort(rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
        y = erf(t_col.ravel())
        kernel = RBF(length_scale=float(10), length_scale_bounds="fixed") + WhiteKernel(noise_level=1e-4)
        self.gp = GaussianProcessRegressor(
            kernel=kernel, random_state=42, normalize_y=True
        ).fit(t_col, y)

    def predict_scalar(self, x):
        t = 6.0 * float(x) - 3.0
        return float(self.gp.predict([[t]])[0])


_surrogate = _Surrogate()


def program(x) -> float:
    return _surrogate.predict_scalar(x)