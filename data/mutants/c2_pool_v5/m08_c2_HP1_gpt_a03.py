import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_poly = PolynomialFeatures(1, include_bias=True)
_Phi = _poly.fit_transform(_t_train)
_reg = LinearRegression().fit(_Phi, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_reg.predict(_poly.transform([[t]]))[0])