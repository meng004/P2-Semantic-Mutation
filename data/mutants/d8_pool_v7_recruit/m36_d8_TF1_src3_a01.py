import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF


def _label(points):
    return (points[:, 0] + points[:, 1] < 0).astype(int)


_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = _label(_X_train)

_model = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])[0, 1])