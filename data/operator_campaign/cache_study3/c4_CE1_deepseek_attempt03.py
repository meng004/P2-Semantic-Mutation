import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())

_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)

_project = lambda v: 6.0 * v - 1.5


def program(x) -> float:
    t = _project(float(x))
    return float(_model.predict([[t]])[0])