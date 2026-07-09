"""Gaussian-process regression surrogate for erf on t = 6x - 3 (mutant)."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

rng42 = np.random.default_rng(42)
T_TRAIN = np.sort(rng42.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
Y_TRAIN = erf(T_TRAIN.ravel())

KERNEL = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-1, noise_level_bounds="fixed")
MODEL = GaussianProcessRegressor(kernel=KERNEL, random_state=42, normalize_y=True)
MODEL.fit(T_TRAIN, Y_TRAIN)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(MODEL.predict([[t]])[0])