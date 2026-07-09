"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_raw = _rng.uniform(low=-3.0, high=3.0, size=300)
_t_train = np.sort(_raw).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())
_params = {"kernel": "rbf", "C": 10.0, "gamma": "scale", "epsilon": 1.0}
_model = SVR(**_params)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    query = np.array([[t]], dtype=float)
    return float(_model.predict(query)[0])