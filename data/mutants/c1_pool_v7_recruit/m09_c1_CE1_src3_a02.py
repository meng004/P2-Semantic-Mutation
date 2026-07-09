"""Surrogate program(x): GPR fit to erf over the mapped test point t = 6x - 3."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _mk_kernel():
    return RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1, noise_level_bounds="fixed")


def _mk_data():
    rng = np.random.default_rng(42)
    t_col = np.sort(rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
    return t_col, erf(t_col.ravel())


_pts, _lbl = _mk_data()
_gp = GaussianProcessRegressor(kernel=_mk_kernel(), random_state=42, normalize_y=True)
_gp.fit(_pts, _lbl)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_gp.predict(np.array([[t]]))[0])