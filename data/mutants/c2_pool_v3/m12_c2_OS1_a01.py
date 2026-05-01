import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import Pipeline

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_basis = SplineTransformer(n_knots=6, degree=3)
_regressor = LinearRegression()
_model = Pipeline(steps=[("basis", _basis), ("regressor", _regressor)])
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    t_val = 4.0 * x_val - 2.0
    query = np.array([[t_val]])
    prediction = _model.predict(query)
    return float(prediction[0])