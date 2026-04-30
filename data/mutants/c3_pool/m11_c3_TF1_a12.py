import numpy as np
from sklearn.neural_network import MLPRegressor


def _target_curve(values):
    scaled = -2.0 * np.asarray(values)
    return 1.0 / (1.0 + np.exp(scaled))


def _make_training_data():
    rng = np.random.default_rng(42)
    raw = rng.uniform(-3.0, 3.0, 100)
    ordered = np.sort(raw)
    return ordered.reshape(-1, 1), _target_curve(ordered)


_features, _labels = _make_training_data()

_net_config = {
    "hidden_layer_sizes": (64, 32),
    "activation": "relu",
    "solver": "adam",
    "max_iter": 5,
    "random_state": 42,
}

_surrogate = MLPRegressor(**_net_config)
_surrogate.fit(_features, _labels)


def program(x) -> float:
    val = float(x)
    mapped = 6.0 * val - 3.0
    point = [[mapped]]
    out = _surrogate.predict(point)
    return float(out[0])