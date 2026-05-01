import numpy as np
from sklearn.neural_network import MLPRegressor as _Net


def _activation_target(u):
    u = np.asarray(u, dtype=float)
    return np.power(1.0 + np.exp(-2.0 * u), -1.0)


def _synthesize_corpus():
    src = np.random.default_rng(42)
    drawn = src.uniform(-3.0, 3.0, 100)
    order = np.sort(drawn)
    feats = order[:, np.newaxis]
    targs = _activation_target(order)
    return feats, targs


_TRAIN_X, _TRAIN_Y = _synthesize_corpus()

_HYPERS = (
    ("hidden_layer_sizes", (64, 32)),
    ("activation", "relu"),
    ("solver", "adam"),
    ("max_iter", 5),
    ("random_state", 42),
)

_net = _Net(**dict(_HYPERS))
_net.fit(_TRAIN_X, _TRAIN_Y)


def program(x) -> float:
    val = float(x)
    mapped = 6.0 * val - 3.0
    payload = np.asarray([[mapped]], dtype=float)
    yhat = _net.predict(payload)
    return float(yhat[0])