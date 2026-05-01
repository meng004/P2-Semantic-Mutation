import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

def _build_training_set(n_samples: int, seed: int):
    generator = np.random.default_rng(seed)
    samples = []
    for _ in range(n_samples):
        samples.append(generator.uniform(0.3, 0.7))
    x_arr = np.array(samples, dtype=float)
    t_arr = np.sort(6.0 * x_arr - 3.0)
    return t_arr.reshape(-1, 1), erf(t_arr)

_T, _Y = _build_training_set(60, 42)

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_T, _Y)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])