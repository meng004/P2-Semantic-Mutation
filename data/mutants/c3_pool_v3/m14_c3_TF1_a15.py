import numpy as np
from sklearn.neural_network import MLPRegressor


def _curve(z):
    z_arr = np.asarray(z, dtype=float)
    result = np.empty_like(z_arr)
    for idx in range(z_arr.shape[0]):
        result[idx] = 1.0 / (1.0 + float(np.exp(-2.0 * z_arr[idx])))
    return result


def _assemble():
    source = np.random.default_rng(42)
    bag = source.uniform(-3.0, 3.0, 100)
    ranked = np.sort(bag)
    return ranked.reshape((-1, 1)), _curve(ranked)


_inputs_train, _targets_train = _assemble()


def _spawn_network():
    params = {}
    params["hidden_layer_sizes"] = (64, 32)
    params["activation"] = "relu"
    params["solver"] = "adam"
    params["random_state"] = 42
    params["max_iter"] = 5
    return MLPRegressor(**params)


_network = _spawn_network()
_network.fit(_inputs_train, _targets_train)


def program(x) -> float:
    s = float(x)
    probe = 6.0 * s - 3.0
    grid = [[probe]]
    out = _network.predict(grid)
    return float(out[0])