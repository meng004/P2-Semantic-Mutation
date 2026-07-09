"""C2: Polynomial Chaos Expansion surrogate — scalar x∈[0,1] interface.

Library: sklearn PolynomialFeatures + LinearRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 4x − 2 ∈ [−2, 2]. Training: tanh(t) (monotone increasing).
Degree-5 polynomial PCE. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


def _collocation_points(n_points):
    rng = np.random.default_rng(42)
    pts = rng.uniform(low=-2.0, high=2.0, size=n_points)
    return np.sort(pts).reshape(-1, 1)


_t_train = _collocation_points(int(80 / 2))
_y_train = np.tanh(_t_train.ravel())

_model = make_pipeline(PolynomialFeatures(5, include_bias=True), LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(_model.predict([[t]])[0])