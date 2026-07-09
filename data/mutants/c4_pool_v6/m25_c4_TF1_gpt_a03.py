import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
_bound = 1.0
xs = np.sort(rng.uniform(-_bound, _bound, 300)).reshape(-1, 1)
ys = np.arctan(3.0 * xs.ravel())

model = KNeighborsRegressor(n_neighbors=7).fit(xs, ys)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(model.predict([[t]])[0])