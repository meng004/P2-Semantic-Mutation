"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_samples = _rng.uniform(-1.0, 1.0, 300)
_t_train = np.sort(_samples).reshape(300, 1)
_y_train = np.tanh(1.5 * _t_train[:, 0])
_model = SVR(kernel="rbf")
_model.set_params(C=10.0, gamma='scale', epsilon=0.01)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    pred = _model.predict([[t]])
    return float(pred[0])