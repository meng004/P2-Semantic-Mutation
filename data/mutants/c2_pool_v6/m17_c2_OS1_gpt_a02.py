import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_spline = SplineTransformer(degree=3, n_knots=6)
_model = make_pipeline(_spline, LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_model.predict([[t]])[0])