import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

_n_points = 40
_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, _n_points)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_model = Pipeline([
    ("poly", PolynomialFeatures(5, include_bias=True)),
    ("lin", LinearRegression()),
])
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_model.predict([[t]])[0])