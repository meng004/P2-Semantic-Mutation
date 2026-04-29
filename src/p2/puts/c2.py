"""C2: Polynomial Chaos Expansion (PCE) surrogate — degree-4 polynomial regression.

Library: sklearn.preprocessing.PolynomialFeatures + sklearn.linear_model.LinearRegression
         (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html

PCE approximation: expand input in polynomial basis, fit coefficients via OLS.
This implements a 1D degree-4 PCE on uniform [−3,3] input space (equivalent to Legendre basis).
Training data (seed=42): 60 points from f(t) = t² + 0.5·sin(3t), t ∈ [−3,3].
program(x): scalar or 1D array of test points → predicted values.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

_DEGREE = 4
_rng = np.random.default_rng(42)
_X_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_y_train = _X_train.ravel() ** 2 + 0.5 * np.sin(3.0 * _X_train.ravel())

_model = make_pipeline(PolynomialFeatures(_DEGREE, include_bias=True), LinearRegression())
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> np.ndarray:
    """Evaluate degree-4 PCE surrogate at test points x; returns array."""
    x = np.asarray(x, dtype=float).ravel().reshape(-1, 1)
    return _model.predict(x)
