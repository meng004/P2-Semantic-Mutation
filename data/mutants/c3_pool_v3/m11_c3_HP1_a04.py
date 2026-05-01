import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid_2t(arr):
    arr = np.asarray(arr, dtype=float)
    out = np.empty_like(arr)
    for i in range(arr.size):
        out.flat[i] = 1.0 / (1.0 + float(np.exp(-2.0 * arr.flat[i])))
    return out


_random_state = np.random.default_rng(42)
_raw_samples = _random_state.uniform(-3.0, 3.0, 100)
_t_axis = np.sort(_raw_samples)
_train_X = _t_axis.reshape((-1, 1))
_train_y = _sigmoid_2t(_t_axis)

_config = {}
_config["hidden_layer_sizes"] = (64, 32)
_config["solver"] = "adam"
_config["max_iter"] = 1000
_config["random_state"] = 42
_config["activation"] = "tanh"

_surrogate = MLPRegressor(**_config)
_surrogate.fit(_train_X, _train_y)


def program(x) -> float:
    val = float(x)
    mapped_t = 6.0 * val - 3.0
    point = [[mapped_t]]
    pred = _surrogate.predict(point)
    return float(pred[0])