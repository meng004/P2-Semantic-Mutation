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


def _build_training_set(n_collocation):
    rng = np.random.default_rng(42)
    raw = rng.uniform(-2.0, 2.0, n_collocation)
    raw.sort()
    return raw.reshape(-1, 1), np.tanh(raw)


_original_n = 80
_t_train, _y_train = _build_training_set(_original_n // 2)

_model = make_pipeline(PolynomialFeatures(5, include_bias=True), LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_model.predict([[t]])[0])