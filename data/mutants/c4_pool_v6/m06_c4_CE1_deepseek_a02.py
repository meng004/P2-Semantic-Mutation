import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_pts = np.sort(_rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
_lab = np.arctan(3.0 * _pts.ravel())

_knn = KNeighborsRegressor(n_neighbors=7)
_knn.fit(_pts, _lab)

_map_params = {"a": 6.0, "b": 1.5}


def program(x) -> float:
    t = _map_params["a"] * float(x) - _map_params["b"]
    return float(_knn.predict([[t]])[0])