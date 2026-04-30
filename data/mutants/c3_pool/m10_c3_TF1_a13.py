import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid_target(arr):
    arr = np.asarray(arr, dtype=float)
    exponent = np.negative(2.0 * arr)
    denom = 1.0 + np.exp(exponent)
    return 1.0 / denom


def _prepare_training_split():
    seeded = np.random.default_rng(42)
    pool = seeded.uniform(low=-3.0, high=3.0, size=100)
    indices = np.argsort(pool)
    sorted_pool = pool[indices]
    feature_matrix = np.reshape(sorted_pool, newshape=(-1, 1))
    label_vector = _sigmoid_target(sorted_pool)
    return feature_matrix, label_vector


_train_X, _train_y = _prepare_training_split()

_layer_topology = (64, 32)
_activation_fn = "relu"
_optimizer = "adam"
_iteration_budget = 5
_seed_value = 42

_estimator = MLPRegressor(
    hidden_layer_sizes=_layer_topology,
    activation=_activation_fn,
    solver=_optimizer,
    max_iter=_iteration_budget,
    random_state=_seed_value,
)
_estimator.fit(_train_X, _train_y)


def program(x) -> float:
    scalar = float(x)
    transformed = 6.0 * scalar - 3.0
    request = np.array([[transformed]], dtype=float)
    response = _estimator.predict(request)
    return float(response[0])