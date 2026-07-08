"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_rbf = RBF(length_scale=10.0, length_scale_bounds="fixed")
_model = GaussianProcessClassifier(kernel=_rbf, random_state=42).fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 1.6 * x - 0.8
    proba = _model.predict_proba([[t, t]])
    return float(proba[0][1])