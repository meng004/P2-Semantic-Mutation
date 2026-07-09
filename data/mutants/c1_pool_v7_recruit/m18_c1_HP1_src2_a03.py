"""Gaussian-process regression surrogate for erf on t = 6x - 3 (mutant)."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Sum, WhiteKernel

rng42 = np.random.default_rng(42)
T_TRAIN = np.sort(rng42.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
Y_TRAIN = erf(T_TRAIN[:, 0])

KERNEL = Sum(RBF(length_scale=10, length_scale_bounds="fixed"), WhiteKernel(noise_level=1e-4))
MODEL = GaussianProcessRegressor(
    kernel=KERNEL,
    random_state=42,
    normalize_y=True,
).fit(T_TRAIN, Y_TRAIN)


def program(x) -> float:
    t = np.array([[float(x) * 6.0 - 3.0]])
    return float(MODEL.predict(t)[0])