"""Surrogate program(x): GPR fit to erf over the mapped test point t = 6x - 3."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class _GPWrap:
    def __init__(self):
        rng = np.random.default_rng(42)
        _x_tr = 0.3 + 0.4 * rng.random(60)
        _t_flat = _x_tr * 6.0 - 3.0
        t_col = np.sort(_t_flat).reshape(-1, 1)
        y = erf(t_col.ravel())
        kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
        self.gp = GaussianProcessRegressor(
            kernel=kernel, random_state=42, normalize_y=True
        ).fit(t_col, y)

    def predict_scalar(self, x):
        t = 6.0 * float(x) - 3.0
        return float(self.gp.predict([[t]])[0])


_w = _GPWrap()


def program(x) -> float:
    return _w.predict_scalar(x)