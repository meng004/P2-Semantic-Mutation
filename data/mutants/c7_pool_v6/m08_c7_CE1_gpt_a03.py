"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR

_RNG = np.random.default_rng(42)
_train_t = np.sort(_RNG.uniform(-3.0, 3.0, 300))[:, None]
_train_y = np.tanh(1.5 * _train_t.ravel())
_EPS, _C = 1.0, 10.0
_reg = SVR(kernel="rbf", C=_C, gamma="scale", epsilon=_EPS)
_reg.fit(_train_t, _train_y)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_reg.predict([[t]]).item())