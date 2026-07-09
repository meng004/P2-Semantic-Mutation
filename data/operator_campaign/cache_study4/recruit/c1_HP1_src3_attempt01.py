"""Surrogate program(x): GPR fit to erf over the mapped test point t = 6x - 3."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_r = np.random.default_rng(42)
_pts = np.sort(_r.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_lbl = erf(_pts.ravel())

_ksum = RBF(length_scale=10.0, length_scale_bounds="fixed") + WhiteKernel(noise_level=1e-4)
_gp = GaussianProcessRegressor(kernel=_ksum, random_state=42, normalize_y=True)
_gp.fit(_pts, _lbl)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_gp.predict([[t]])[0])