import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def _generate_training_data():
    generator = np.random.default_rng(42)
    points = generator.uniform(-3.0, 3.0, 60)
    indices = np.argsort(points)
    sorted_points = points[indices]
    return sorted_points.reshape(60, 1), erf(sorted_points)


def _assemble_kernel():
    rbf_part = RBF(length_scale=1.0)
    white_part = WhiteKernel(noise_level=1e-1)
    return rbf_part + white_part


_t_train, _y_train = _generate_training_data()
_model = GaussianProcessRegressor(
    kernel=_assemble_kernel(),
    random_state=42,
    normalize_y=True,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    val = float(x)
    t = 6.0 * val - 3.0
    test_input = [[t]]
    result = _model.predict(test_input)
    return float(result[0])