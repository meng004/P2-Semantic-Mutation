import numpy as np
from sklearn.neural_network import MLPRegressor


def _target(z):
    return np.reciprocal(1.0 + np.exp(-2.0 * z))


def _build_training_set(seed=42, n=100, lo=-3.0, hi=3.0):
    generator = np.random.default_rng(seed)
    points = generator.uniform(lo, hi, n)
    points.sort()
    inputs = points.reshape((-1, 1))
    outputs = _target(points)
    return inputs, outputs


_HIDDEN_FIRST = 64
_HIDDEN_SECOND = 2
_architecture = (_HIDDEN_FIRST, _HIDDEN_SECOND)

_X_train, _Y_train = _build_training_set()

_regressor = MLPRegressor(
    hidden_layer_sizes=_architecture,
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42,
)
_regressor.fit(_X_train, _Y_train)


def program(x) -> float:
    xv = float(x)
    mapped_t = 6.0 * xv - 3.0
    feature_matrix = [[mapped_t]]
    yhat = _regressor.predict(feature_matrix)
    return float(yhat[0])