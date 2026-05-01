import numpy as np
from sklearn.neural_network import MLPRegressor


def _logistic(values):
    return np.reciprocal(1.0 + np.exp(np.multiply(-2.0, values)))


_generator = np.random.default_rng(42)
_raw_samples = _generator.uniform(-3.0, 3.0, 100)
_t_train = np.sort(_raw_samples)[:, np.newaxis]
_y_train = _logistic(_t_train.ravel())

_regressor_kwargs = dict(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=5,
    random_state=42,
)
_model = MLPRegressor(**_regressor_kwargs).fit(_t_train, _y_train)


def program(x) -> float:
    scalar_x = float(x)
    query_t = 6.0 * scalar_x - 3.0
    prediction = _model.predict(np.array([[query_t]]))
    return float(prediction[0])