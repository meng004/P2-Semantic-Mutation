import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer

_rng = np.random.default_rng(42)

_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80))[:, None]
_y_train = np.tanh(_t_train[:, 0])

_model = Pipeline(
    steps=[
        ("features", SplineTransformer(n_knots=6, degree=3)),
        ("regressor", LinearRegression()),
    ]
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 4.0 * float(x) - 2.0
    prediction = _model.predict(np.array([[t]], dtype=float))
    return float(prediction[0])