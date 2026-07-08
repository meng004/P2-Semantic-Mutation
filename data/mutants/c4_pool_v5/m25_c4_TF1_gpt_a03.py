"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor


def _make_training():
    rng = np.random.default_rng(42)
    tt = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
    return tt, np.arctan(3.0 * tt.ravel())


_t_train, _y_train = _make_training()
_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])