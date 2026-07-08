"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_TRAIN_LO, _TRAIN_HI = -1.0, 1.0
_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(_TRAIN_LO, _TRAIN_HI, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())

_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])