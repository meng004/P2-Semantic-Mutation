"""C7: Support-Vector regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.svm.SVR (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x-3 ∈ [-3,3]. Training: tanh(1.5t) (monotone, odd, bounded).
RBF-kernel epsilon-SVR surrogate. Returns scalar prediction, monotone in x.
"""
import numpy as np
from sklearn.svm import SVR

_rng = np.random.default_rng(42)
_t_samples = _rng.uniform(-3.0, 3.0, 300)
_t_train = np.sort(_t_samples).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())

_svr_config = {
    "kernel": "rbf",
    "C": 10.0,
    "gamma": "scale",
    "epsilon": 1.0,
}
_model = SVR(**_svr_config)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    prediction = _model.predict([[t]])
    return float(prediction[0])