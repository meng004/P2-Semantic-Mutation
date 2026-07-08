"""C7 SVR surrogate (mutant: wide epsilon tube)."""
import numpy as np
from sklearn.svm import SVR

_EPS = 1.0
_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())

_model = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=_EPS)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict(np.array([[t]]))[0])