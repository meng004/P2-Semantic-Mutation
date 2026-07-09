import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_range = (-1.0, 1.0)
_pts = np.sort(_rng.uniform(_range[0], _range[1], 300)).reshape(-1, 1)
_lab = np.arctan(3.0 * _pts.ravel())

_knn = KNeighborsRegressor(n_neighbors=7)
_knn.fit(_pts, _lab)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_knn.predict([[t]])[0])