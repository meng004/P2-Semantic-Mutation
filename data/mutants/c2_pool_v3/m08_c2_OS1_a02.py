import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_spline = SplineTransformer(n_knots=6, degree=3)
_features_train = _spline.fit_transform(_t_train)
_lr = LinearRegression()
_lr.fit(_features_train, _y_train)


def program(x) -> float:
    xf = float(x)
    t = 4.0 * xf - 2.0
    feats = _spline.transform([[t]])
    yhat = _lr.predict(feats)[0]
    return float(yhat)