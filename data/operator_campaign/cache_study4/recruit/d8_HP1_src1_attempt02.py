import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

_gen = np.random.default_rng(42)
_X_train = _gen.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_kernel = RBF(10.0, "fixed")
_model = GaussianProcessClassifier(kernel=_kernel, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[1.6 * x - 0.8, 1.6 * x - 0.8]])[0, 1])