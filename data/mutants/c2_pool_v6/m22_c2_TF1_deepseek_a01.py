import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

_rng = np.random.default_rng(42)
_samples = _rng.uniform(-2.0, 2.0, 40)
_t_train = np.sort(_samples).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_model = make_pipeline(PolynomialFeatures(5, include_bias=True), LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    query = np.array([[t]], dtype=float)
    return float(_model.predict(query)[0])