import numpy as np
from sklearn.neural_network import MLPRegressor as _MLP


def _target(values):
    arr = np.asarray(values, dtype=float)
    return np.reciprocal(1.0 + np.exp(-2.0 * arr))


def _make_dataset():
    generator = np.random.default_rng(42)
    raw = generator.uniform(-3.0, 3.0, size=100)
    ordered = np.sort(raw)
    feature_matrix = ordered[:, None]
    response = _target(ordered)
    return feature_matrix, response


_features, _labels = _make_dataset()

_ACTIVATION_CHOICE = "tanh"

_regressor = _MLP(
    hidden_layer_sizes=(64, 32),
    activation=_ACTIVATION_CHOICE,
    solver="adam",
    max_iter=1000,
    random_state=42,
)
_regressor.fit(_features, _labels)


def program(x) -> float:
    scalar = float(x)
    mapped = 6.0 * scalar - 3.0
    query = np.array([[mapped]], dtype=float)
    yhat = _regressor.predict(query)
    return float(yhat[0])