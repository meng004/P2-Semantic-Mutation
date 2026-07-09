import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = GaussianProcessClassifier(kernel=RBF(length_scale=1e1, length_scale_bounds="fixed"), random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    f = 1.6 * float(x) - 0.8
    return float(_model.predict_proba([[f, f]])[0, 1])