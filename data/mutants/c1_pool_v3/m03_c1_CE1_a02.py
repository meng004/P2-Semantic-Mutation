"""C1: Gaussian Process Regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.gaussian_process.GaussianProcessRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: erf(t) (monotone increasing).
Returns scalar GPR prediction at t. Monotone in x (erf is monotone).
"""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_SEED = 42
_N_TRAIN = 60
_T_LO, _T_HI = -3.0, 3.0
_NOISE = 1e-1
_LENGTH_SCALE = 1.0


def _make_design_matrix(seed, n, lo, hi):
    generator = np.random.default_rng(seed)
    raw = generator.uniform(lo, hi, n)
    ordered = np.sort(raw)
    return ordered[:, None], erf(ordered)


_X, _Y = _make_design_matrix(_SEED, _N_TRAIN, _T_LO, _T_HI)

_composite_kernel = RBF(length_scale=_LENGTH_SCALE) + WhiteKernel(noise_level=_NOISE)
_gpr = GaussianProcessRegressor(
    kernel=_composite_kernel,
    random_state=_SEED,
    normalize_y=True,
)
_gpr.fit(_X, _Y)


def program(x) -> float:
    xv = float(x)
    t_query = 6.0 * xv - 3.0
    query = np.asarray([[t_query]], dtype=float)
    yhat = _gpr.predict(query)
    return float(yhat[0])