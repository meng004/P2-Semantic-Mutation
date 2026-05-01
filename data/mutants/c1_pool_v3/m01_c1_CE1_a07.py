import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

NOISE = 1e-1
LENGTH = 1.0
SEED = 42
N = 60


def _make_data(seed, n):
    gen = np.random.default_rng(seed)
    pts = gen.uniform(low=-3.0, high=3.0, size=n)
    pts.sort()
    return pts[:, None], erf(pts)


def _make_kernel(ls, nl):
    k = RBF(length_scale=ls)
    k += WhiteKernel(noise_level=nl)
    return k


_X, _y = _make_data(SEED, N)
_gpr = GaussianProcessRegressor(
    kernel=_make_kernel(LENGTH, NOISE),
    random_state=SEED,
    normalize_y=True,
).fit(_X, _y)


def program(x) -> float:
    xv = float(x)
    t = 6.0 * xv - 3.0
    grid = np.asarray([[t]], dtype=float)
    yhat = _gpr.predict(grid)
    return float(yhat.ravel()[0])