import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


_SEED = 42
_N_TRAIN = 60
_T_LO, _T_HI = -3.0, 3.0
_LENGTH_SCALE = 1.0
_NOISE_LEVEL = 1e-1


def _generate_sorted_inputs(seed: int, count: int, lo: float, hi: float) -> np.ndarray:
    generator = np.random.default_rng(seed)
    raw = generator.uniform(lo, hi, count)
    return np.sort(raw)


def _assemble_kernel(length_scale: float, noise_level: float):
    rbf_part = RBF(length_scale=length_scale)
    white_part = WhiteKernel(noise_level=noise_level)
    composite = rbf_part + white_part
    return composite


def _train_surrogate():
    t_sorted = _generate_sorted_inputs(_SEED, _N_TRAIN, _T_LO, _T_HI)
    X_train = t_sorted[:, np.newaxis]
    y_train = erf(t_sorted)
    kernel = _assemble_kernel(_LENGTH_SCALE, _NOISE_LEVEL)
    estimator = GaussianProcessRegressor(
        kernel=kernel,
        random_state=_SEED,
        normalize_y=True,
    )
    estimator.fit(X_train, y_train)
    return estimator


_model = _train_surrogate()


def program(x) -> float:
    x_scalar = float(x)
    t_eval = 6.0 * x_scalar - 3.0
    input_point = np.array([[t_eval]])
    prediction_arr = _model.predict(input_point)
    return float(prediction_arr[0])