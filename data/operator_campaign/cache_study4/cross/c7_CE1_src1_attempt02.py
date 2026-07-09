import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_t_samples = _rng.uniform(-3.0, 3.0, 300)
_t_train = np.sort(_t_samples)[:, None]
_y_train = np.tanh(1.5 * _t_train[:, 0])

_svr_params = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "epsilon": 1.0,
}
_model = SVR(**_svr_params)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    prediction = _model.predict(np.array([[t]], dtype=float))
    return float(prediction[0])