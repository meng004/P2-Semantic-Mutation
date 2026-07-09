import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
xs = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
ys = np.arctan(3.0 * xs.ravel())

k = 7 - 6
model = KNeighborsRegressor(n_neighbors=k).fit(xs, ys)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(model.predict([[t]])[0])