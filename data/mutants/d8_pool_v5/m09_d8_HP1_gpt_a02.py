"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_ls = 5.0 * 2.0  # 10.0
_model = GaussianProcessClassifier(
    kernel=RBF(length_scale=_ls, length_scale_bounds="fixed"), random_state=42)
_model = _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba(np.array([[1.6 * x - 0.8, 1.6 * x - 0.8]]))[0, 1])