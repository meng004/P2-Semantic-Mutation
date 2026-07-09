import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
_half_width = 1.0
train_t = np.sort(_half_width * (2.0 * rng.random(300) - 1.0)).reshape(-1, 1)
train_y = np.arctan(3.0 * train_t.ravel())

reg = KNeighborsRegressor(n_neighbors=7)
reg.fit(train_t, train_y)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(reg.predict(np.array([[t]]))[0])