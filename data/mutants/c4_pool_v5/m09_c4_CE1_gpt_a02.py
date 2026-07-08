"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())

_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)


def _to_test_point(x):
    scale, shift = 6.0, 1.5
    return scale * x - shift


def program(x) -> float:
    t = _to_test_point(float(x))
    return float(_model.predict([[t]])[0])