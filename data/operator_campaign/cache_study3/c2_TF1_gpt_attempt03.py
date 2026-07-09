import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

_N_FULL = 80
_N_COLLOCATION = _N_FULL // 2
_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, _N_COLLOCATION)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_model = Pipeline([
    ("poly", PolynomialFeatures(5, include_bias=True)),
    ("lin", LinearRegression()),
])
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(_model.predict([[t]])[0])