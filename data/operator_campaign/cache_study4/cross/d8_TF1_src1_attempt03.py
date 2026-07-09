import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, size=(400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] < 0).astype(int)

_kernel = RBF(length_scale=1.0)
_model = GaussianProcessClassifier(kernel=_kernel, random_state=42)
_model.fit(_X_train, _y_train)


def _features(x):
    z = 1.6 * float(x) - 0.8
    return [[z, z]]


def program(x):
    return float(_model.predict_proba(_features(x))[0, 1])