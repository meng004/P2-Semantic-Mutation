import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
xs = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
ys = np.arctan(3.0 * xs.ravel())

model = KNeighborsRegressor(n_neighbors=7).fit(xs, ys)

shift = 1.5


def program(x) -> float:
    t = 6.0 * float(x) - shift
    q = np.array([[t]])
    return float(model.predict(q)[0])