"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR

def _build():
    r = np.random.default_rng(42)
    t = np.sort(r.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    y = np.tanh(1.5 * t.ravel())
    return SVR(kernel="rbf", C=0.01, gamma="scale", epsilon=0.01).fit(t, y)

_model = _build()


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    out = _model.predict([[t]])
    return float(np.asarray(out).ravel()[0])