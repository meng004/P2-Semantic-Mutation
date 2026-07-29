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

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel()) + 0.05  # Erode odd symmetry with a constant offset

_model = make_pipeline(PolynomialFeatures(5, include_bias=True), LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_model.predict([[t]])[0])