import numpy as np
from sklearn.neural_network import MLPRegressor
from functools import reduce


_SEED = 42
_N = 100
_HIDDEN = (64, 32)
_MAX_ITER = 5


def _sigmoid_2t(values):
    arr = np.asarray(values, dtype=float)
    scaled = np.multiply(arr, 2.0)
    negated = np.negative(scaled)
    denom = reduce(lambda a, b: a + b, [1.0, np.exp(negated)])
    return 1.0 / denom


def _draw_sorted_uniform(seed, lo, hi, count):
    gen = np.random.default_rng(seed)
    pool = gen.uniform(lo, hi, count)
    indices = np.argsort(pool)
    return pool[indices]


_t_flat = _draw_sorted_uniform(_SEED, -3.0, 3.0, _N)
_t_matrix = _t_flat[:, np.newaxis]
_y_vector = _sigmoid_2t(_t_flat)


def _make_network():
    params = {
        "hidden_layer_sizes": _HIDDEN,
        "activation": "relu",
        "solver": "adam",
        "max_iter": _MAX_ITER,
        "random_state": _SEED,
    }
    estimator = MLPRegressor(**params)
    return estimator


_model = _make_network()
_model.fit(_t_matrix, _y_vector)


def program(x) -> float:
    x_val = float(x)
    t_input = 6.0 * x_val - 3.0
    feature = np.array([[t_input]], dtype=float)
    pred = _model.predict(feature)
    return float(pred[0])