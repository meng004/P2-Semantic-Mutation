"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_col_sum = _X_train[:, 0] + _X_train[:, 1]
_y_train = np.where(_col_sum < 0, 1, 0)

_model = GaussianProcessClassifier(kernel=RBF(length_scale=1.0), random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    feat = 1.6 * x - 0.8
    return float(_model.predict_proba([[feat, feat]])[0, 1])