"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())


class _Surrogate:
    def __init__(self):
        self.m = KNeighborsRegressor(n_neighbors=1)
        self.m.fit(_t_train, _y_train)

    def eval(self, t):
        return float(self.m.predict([[t]])[0])


_surrogate = _Surrogate()


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return _surrogate.eval(t)