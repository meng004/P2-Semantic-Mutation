"""C4: k-Nearest-Neighbours regressor surrogate — scalar x∈[0,1] interface.

Library: sklearn.neighbors.KNeighborsRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x-3 ∈ [-3,3]. Training: arctan(3t) (monotone, odd).
7-neighbour instance-based surrogate. Returns scalar prediction, monotone in x.
"""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(2026)
_t_train = np.sort(_rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
_y_train = np.arctan(3.0 * _t_train.ravel())

_model = KNeighborsRegressor(n_neighbors=7)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])