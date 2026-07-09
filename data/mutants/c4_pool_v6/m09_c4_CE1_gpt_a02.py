import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
train_t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
train_y = np.arctan(3.0 * train_t.ravel())

reg = KNeighborsRegressor(n_neighbors=7)
reg.fit(train_t, train_y)


def program(x) -> float:
    x = float(x)
    t = 6.0 * (x - 0.25)
    return float(reg.predict(np.array([[t]]))[0])