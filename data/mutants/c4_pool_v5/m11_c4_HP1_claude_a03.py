"""C4 kNN surrogate mutant."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor


def _build(k):
    rng = np.random.default_rng(42)
    tt = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    yy = np.arctan(3.0 * tt.ravel())
    m = KNeighborsRegressor(n_neighbors=k)
    m.fit(tt, yy)
    return m


_model = _build(1)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])