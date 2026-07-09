import numpy as np
from sklearn.neighbors import KNeighborsRegressor

rng = np.random.default_rng(42)
t_train = np.sort(rng.uniform(-1.0, 1.0, 300)).reshape(-1, 1)
y_train = np.arctan(3.0 * t_train.ravel())

knn = KNeighborsRegressor(n_neighbors=7)
knn.fit(t_train, y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(knn.predict([[t]])[0])