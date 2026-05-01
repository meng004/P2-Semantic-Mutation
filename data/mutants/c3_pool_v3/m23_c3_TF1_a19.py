import numpy as np
from sklearn.neural_network import MLPRegressor
from functools import partial


def _double_logistic(u):
    u = np.asarray(u, dtype=float)
    exponent = -2.0 * u
    return 1.0 / (1.0 + np.exp(exponent))


_seed_value = 42
_n_points = 100
_lo, _hi = -3.0, 3.0

_uniform_sampler = partial(np.random.default_rng(_seed_value).uniform, _lo, _hi)
_raw_samples = _uniform_sampler(_n_points)
_sorted_samples = np.sort(_raw_samples)

_X_train = _sorted_samples[:, np.newaxis]
_y_train = _double_logistic(_sorted_samples)


def _make_mlp():
    base_config = {
        "hidden_layer_sizes": (64, 32),
        "activation": "relu",
        "solver": "adam",
    }
    extra_config = {
        "max_iter": 5,
        "random_state": _seed_value,
    }
    merged = {**base_config, **extra_config}
    return MLPRegressor(**merged)


_surrogate = _make_mlp()
_surrogate.fit(_X_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    t_point = 6.0 * x_val - 3.0
    query_matrix = np.asarray([[t_point]], dtype=float)
    y_hat = _surrogate.predict(query_matrix)
    return float(y_hat[0])