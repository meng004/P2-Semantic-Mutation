import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid_response(arr):
    exponent = -2.0 * arr
    denom = 1.0 + np.exp(exponent)
    return 1.0 / denom


def _layer_spec():
    spec = {"first": 64, "second": 2}
    return (spec["first"], spec["second"])


_seed_value = 42
_sample_count = 100

_prng = np.random.default_rng(_seed_value)
_unsorted = _prng.uniform(-3.0, 3.0, _sample_count)
_sorted_idx = np.argsort(_unsorted)
_sorted_t = _unsorted[_sorted_idx]
_X_matrix = _sorted_t.reshape(-1, 1)
_y_vector = _sigmoid_response(_sorted_t)

_net = MLPRegressor(
    hidden_layer_sizes=_layer_spec(),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=_seed_value,
)
_net.fit(_X_matrix, _y_vector)


def program(x) -> float:
    x_scalar = float(x)
    t_point = 6.0 * x_scalar - 3.0
    feature = np.array([t_point]).reshape(1, 1)
    yhat = _net.predict(feature)
    return float(yhat[0])