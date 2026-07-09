import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_transformer = PolynomialFeatures(degree=1, include_bias=True)
_design = _transformer.fit_transform(_t_train)
_estimator = LinearRegression()
_estimator.fit(_design, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    row = _transformer.transform([[t]])
    return float(_estimator.predict(row).item())