"""Gaussian-process regression surrogate for erf on t = 6x - 3 (mutant)."""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def make_kernel():
    return RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1, noise_level_bounds="fixed")


def make_training_data():
    rng = np.random.default_rng(42)
    t_col = np.sort(rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
    return t_col, erf(t_col.ravel())


T_TRAIN, Y_TRAIN = make_training_data()
MODEL = GaussianProcessRegressor(kernel=make_kernel(), random_state=42, normalize_y=True)
MODEL.fit(T_TRAIN, Y_TRAIN)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(MODEL.predict(np.array([[t]]))[0])