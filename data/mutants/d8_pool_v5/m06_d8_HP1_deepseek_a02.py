"""D8: Gaussian Process classifier - scalar x in [0,1] interface."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

LENGTH = 10.0

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = GaussianProcessClassifier(
    RBF(length_scale=LENGTH, length_scale_bounds="fixed"), random_state=42)
_model.fit(_X_train, _y_train)


def program(x):
    x = float(x)
    feat = 1.6 * x - 0.8
    return float(_model.predict_proba([[feat, feat]])[0, 1])