"""C7 SVR surrogate."""
import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())

_model = SVR(kernel="rbf", gamma="scale", epsilon=0.01)
_model.set_params(C=0.01)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict([[t]])[0])