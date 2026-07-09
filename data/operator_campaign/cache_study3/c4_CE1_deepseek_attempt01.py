import numpy as np
from sklearn.neighbors import KNeighborsRegressor

generator = np.random.default_rng(42)
grid = np.sort(generator.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
targets = np.arctan(3.0 * grid.ravel())

surrogate = KNeighborsRegressor(n_neighbors=7)
surrogate.fit(grid, targets)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 1.5
    return float(surrogate.predict([[t]])[0])