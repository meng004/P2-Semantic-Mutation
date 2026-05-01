import numpy as np
from sklearn.neural_network import MLPRegressor


SEED = 42
N_TRAIN = 100


def _make_targets(t_values):
    result = []
    for ti in t_values.tolist():
        result.append(1.0 / (1.0 + np.exp(-2.0 * ti)))
    return np.array(result, dtype=float)


def _gather_train_points():
    r = np.random.default_rng(SEED)
    raw = r.uniform(-3.0, 3.0, N_TRAIN)
    ordered = np.array(sorted(raw.tolist()), dtype=float)
    return ordered


_t_axis = _gather_train_points()
_X_train = _t_axis.reshape((-1, 1))
_y_train = _make_targets(_t_axis)


def _spawn_mlp():
    hp = [
        ("hidden_layer_sizes", (64, 32)),
        ("activation", "relu"),
        ("solver", "adam"),
        ("max_iter", 5),
        ("random_state", SEED),
    ]
    return MLPRegressor(**dict(hp))


_net = _spawn_mlp()
_net.fit(_X_train, _y_train)


def program(x) -> float:
    xf = float(x)
    t_point = 6.0 * xf - 3.0
    arr = np.array([t_point], dtype=float).reshape(1, 1)
    yhat = _net.predict(arr)
    return float(yhat[0])