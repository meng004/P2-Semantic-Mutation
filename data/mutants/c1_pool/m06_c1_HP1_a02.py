import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _build_training_set(seed: int, n: int):
    gen = np.random.default_rng(seed)
    raw = gen.uniform(-3.0, 3.0, n)
    ordered = np.sort(raw)
    inputs = ordered[:, None]
    targets = erf(ordered)
    return inputs, targets


def _make_kernel(base_length_scale):
    scaled_length_scale = base_length_scale
    for _ in range(1):
        scaled_length_scale = scaled_length_scale * 10
    smooth_part = RBF(length_scale=scaled_length_scale)
    noise_part = WhiteKernel(noise_level=1e-4)
    return smooth_part + noise_part


_SEED = 42
_X_TRAIN, _Y_TRAIN = _build_training_set(_SEED, 60)
_KERNEL = _make_kernel(1.0)

_model = GaussianProcessRegressor(
    kernel=_KERNEL,
    random_state=_SEED,
    normalize_y=True,
)
_model.fit(_X_TRAIN, _Y_TRAIN)


def program(x) -> float:
    val = float(x)
    t_point = 6.0 * val - 3.0
    grid = [[t_point]]
    mu = _model.predict(grid)
    return float(mu[0])