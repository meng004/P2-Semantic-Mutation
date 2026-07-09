import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_pts = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_lab = np.arctan(3.0 * _pts.ravel())

_knn = KNeighborsRegressor(n_neighbors=1, weights="uniform")
_knn.fit(_pts, _lab)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_knn.predict([[t]])[0])