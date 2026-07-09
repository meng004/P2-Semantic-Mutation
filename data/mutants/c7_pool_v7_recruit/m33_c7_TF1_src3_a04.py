"""C7: Support-Vector regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.svm.SVR (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x-3 ∈ [-3,3]. Training: tanh(1.5t) (monotone, odd, bounded).
RBF-kernel epsilon-SVR surrogate. Returns scalar prediction, monotone in x.
"""
import numpy as np
from sklearn.svm import SVR


def _make_training_set():
    rng = np.random.default_rng(42)
    t = np.sort(2.0 * rng.uniform(0.0, 1.0, 300) - 1.0).reshape(-1, 1)
    y = np.tanh(1.5 * t.ravel())
    return t, y


_t_train, _y_train = _make_training_set()

_model = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=0.01)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict([[t]])[0])