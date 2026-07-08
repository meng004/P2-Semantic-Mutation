"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())

_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    # factored form of 6*x - 1.5
    t = 6.0 * (x - 0.25)
    q = np.array([[t]], dtype=float)
    return float(_model.predict(q)[0])