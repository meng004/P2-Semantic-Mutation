import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer

rng = np.random.default_rng(42)
t_grid = np.sort(rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
y_grid = np.tanh(t_grid.ravel())

surrogate = make_pipeline(SplineTransformer(n_knots=6, degree=3), LinearRegression())
surrogate.fit(t_grid, y_grid)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(surrogate.predict([[t]])[0])