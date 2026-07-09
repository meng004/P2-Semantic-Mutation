"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR


def _train_points(n=300):
    rng = np.random.default_rng(42)
    return np.sort(rng.uniform(-3.0, 3.0, n)).reshape(-1, 1)


_t_train = _train_points()
_y_train = np.tanh(1.5 * _t_train.ravel())
_model = SVR(kernel="rbf", C=0.01, gamma="scale", epsilon=0.01)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])