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
from sklearn.preprocessing import SplineTransformer


def _build_surrogate():
    rng = np.random.default_rng(42)
    t_train = np.sort(rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
    y_train = np.tanh(t_train.ravel())
    basis = SplineTransformer(n_knots=6, degree=3)
    surrogate = make_pipeline(basis, LinearRegression())
    surrogate.fit(t_train, y_train)
    return surrogate


_model = _build_surrogate()


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    return float(_model.predict(np.array([[t]]))[0])