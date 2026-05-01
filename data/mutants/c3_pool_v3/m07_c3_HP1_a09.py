import numpy as np
from sklearn.neural_network import MLPRegressor
from functools import reduce


def _sigmoid_of_two_t(t):
    t = np.asarray(t, dtype=float)
    neg_two_t = reduce(lambda a, b: a * b, [-1.0, 2.0, t])
    return 1.0 / (1.0 + np.exp(neg_two_t))


def _training_inputs():
    generator = np.random.default_rng(42)
    raw = generator.uniform(-3.0, 3.0, 100)
    ordered = np.sort(raw)
    return ordered


_t_sorted = _training_inputs()
_X_train = _t_sorted.reshape((-1, 1))
_y_train = _sigmoid_of_two_t(_t_sorted)


_param_keys = ("hidden_layer_sizes", "activation", "solver", "max_iter", "random_state")
_param_vals = ((64, 32), "tanh", "adam", 1000, 42)
_mlp_kwargs = {k: v for k, v in zip(_param_keys, _param_vals)}


_surrogate = MLPRegressor(**_mlp_kwargs)
_surrogate.fit(_X_train, _y_train)


def program(x) -> float:
    x_as_float = float(x)
    t_point = 6.0 * x_as_float - 3.0
    feature = np.array([[t_point]], dtype=float)
    yhat = _surrogate.predict(feature)
    return float(yhat[0])