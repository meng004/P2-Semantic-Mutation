"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR

_hyper = dict(kernel='rbf', C=10.0, gamma='scale', epsilon=1.0)
_g = np.random.default_rng(42)
_T = np.sort(_g.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_Y = np.tanh(1.5 * _T.ravel())
_svr = SVR(**_hyper).fit(_T, _Y)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_svr.predict(np.array([[t]]))[0])