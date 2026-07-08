"""C7 SVR surrogate (wide insensitive tube)."""
import numpy as np
from sklearn.svm import SVR


class _Surrogate:
    def __init__(self):
        rng = np.random.default_rng(42)
        self.t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
        self.y = np.tanh(1.5 * self.t.ravel())
        self.m = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=1.0)
        self.m.fit(self.t, self.y)

    def eval(self, t):
        return float(self.m.predict([[t]])[0])


_surr = _Surrogate()


def program(x) -> float:
    return _surr.eval(6.0 * float(x) - 3.0)