"""Surrogate program(x): GPR fit to erf over the mapped test point t = 6x - 3."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Sum, WhiteKernel

_r = np.random.default_rng(42)
_u = _r.random(60)
_pts = np.sort(-1.2 + 2.4 * _u).reshape(-1, 1)
_lbl = erf(_pts[:, 0])

_ksum = Sum(RBF(length_scale=1.0), WhiteKernel(noise_level=1e-4))
_gp = GaussianProcessRegressor(
    kernel=_ksum,
    random_state=42,
    normalize_y=True,
).fit(_pts, _lbl)


def program(x) -> float:
    t = np.array([[float(x) * 6.0 - 3.0]])
    return float(_gp.predict(t)[0])