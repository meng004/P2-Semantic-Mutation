"""C7 SVR surrogate of tanh(1.5t), t=6x-3, x in [0,1]."""
import numpy as np
from sklearn.svm import SVR


class _Surrogate:
    def __init__(self):
        rng = np.random.default_rng(42)
        self.T = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
        self.Y = np.tanh(1.5 * self.T.ravel())
        self.m = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=1.0)
        self.m.fit(self.T, self.Y)
    def __call__(self, t):
        return float(self.m.predict([[t]])[0])


_surrogate = _Surrogate()


def program(x) -> float:
    return _surrogate(6.0 * float(x) - 3.0)