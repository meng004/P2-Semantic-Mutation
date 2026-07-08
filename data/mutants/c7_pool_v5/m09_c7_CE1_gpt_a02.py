"""C7 SVR surrogate (epsilon widened)."""
import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())

_model = SVR(epsilon=1.0, C=10.0, kernel="rbf", gamma="scale")
_model.fit(_t_train, _y_train)


def program(x) -> float:
    val = float(x)
    t = 6.0 * val - 3.0
    pt = [[t]]
    return float(_model.predict(pt)[0])