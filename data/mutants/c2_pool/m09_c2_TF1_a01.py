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

_n_pts = 40
_rng = np.random.default_rng(42)
_samples = _rng.uniform(-2.0, 2.0, _n_pts)
_t_train = np.sort(_samples)[:, np.newaxis]
_y_train = np.tanh(_t_train).ravel()

_pipeline_steps = [PolynomialFeatures(degree=5, include_bias=True), LinearRegression()]
_model = make_pipeline(*_pipeline_steps)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    xv = float(x)
    t_eval = 4.0 * xv - 2.0
    pred = _model.predict(np.array([[t_eval]]))
    return float(pred[0])