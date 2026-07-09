"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR


def _make_surrogate():
    rng = np.random.default_rng(42)
    tt = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    yy = np.tanh(1.5 * tt.ravel())
    m = SVR(kernel="rbf", C=0.01, gamma="scale", epsilon=0.01)
    m.fit(tt, yy)
    return m


_surrogate = _make_surrogate()


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_surrogate.predict([[t]])[0])