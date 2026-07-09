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
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.tanh(1.5 * _t_train.ravel())

def _build_surrogate():
    est = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=1.0)
    est.fit(_t_train, _y_train)
    return est


_model = _build_surrogate()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])