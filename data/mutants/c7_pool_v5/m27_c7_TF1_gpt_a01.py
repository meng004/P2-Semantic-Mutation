"""C7 support vector regression surrogate."""
import numpy as np
from sklearn.svm import SVR


def _build():
    rng = np.random.default_rng(42)
    tt = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
    yy = np.tanh(1.5 * tt.ravel())
    m = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=0.01)
    m.fit(tt, yy)
    return m


_model = _build()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])