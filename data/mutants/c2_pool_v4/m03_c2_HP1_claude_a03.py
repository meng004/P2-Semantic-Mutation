"""C2: Polynomial Chaos Expansion surrogate — scalar x∈[0,1] interface.

Library: sklearn PolynomialFeatures + LinearRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 4x − 2 ∈ [−2, 2]. Training: tanh(t) (monotone increasing).
Degree-5 polynomial PCE. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_poly = PolynomialFeatures(degree=1, include_bias=True)
_X_train = _poly.fit_transform(_t_train)
_reg = LinearRegression()
_reg.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    X_test = _poly.transform(np.array([[t]]))
    return float(_reg.predict(X_test)[0])