import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid_target(t_vec):
    t_vec = np.asarray(t_vec, dtype=float)
    return 1.0 / (1.0 + np.exp(np.negative(2.0 * t_vec)))


def _prepare_dataset():
    seed = 42
    size = 100
    low, high = -3.0, 3.0
    rng_obj = np.random.default_rng(seed)
    raw_t = rng_obj.uniform(low, high, size)
    sorted_t = np.sort(raw_t)
    feature_matrix = sorted_t[..., np.newaxis]
    target_vector = _sigmoid_target(sorted_t)
    return feature_matrix, target_vector


_X_train, _y_train = _prepare_dataset()


_HYPERPARAMS = [
    ("activation", "tanh"),
    ("hidden_layer_sizes", (64, 32)),
    ("max_iter", 1000),
    ("random_state", 42),
    ("solver", "adam"),
]


def _build_model(param_pairs):
    config = {}
    idx = 0
    while idx < len(param_pairs):
        k, v = param_pairs[idx]
        config[k] = v
        idx += 1
    return MLPRegressor(**config)


_net = _build_model(_HYPERPARAMS)
_net.fit(_X_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    t_val = 6.0 * x_val - 3.0
    query = [[t_val]]
    out = _net.predict(query)
    return float(out[0])