import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(42)
t_grid = np.sort(rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
y_grid = np.tanh(t_grid.ravel())

pce = make_pipeline(PolynomialFeatures(1, include_bias=True), LinearRegression())
pce.fit(t_grid, y_grid)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(pce.predict([[t]])[0])