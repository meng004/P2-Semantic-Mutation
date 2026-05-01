import numpy as np
from sklearn.neural_network import MLPRegressor


_SEED = 42
_N_SAMPLES = 100
_T_LOW, _T_HIGH = -3.0, 3.0


def _logistic_2t(z):
    z_arr = np.asarray(z, dtype=float)
    return 1.0 / (1.0 + np.exp(-2.0 * z_arr))


def _sample_training_points():
    gen = np.random.default_rng(_SEED)
    pts = gen.uniform(_T_LOW, _T_HIGH, _N_SAMPLES)
    return np.sort(pts)


_t_sorted = _sample_training_points()
_X_train = _t_sorted[:, np.newaxis]
_y_train = _logistic_2t(_t_sorted)

_hyperparams = {
    "hidden_layer_sizes": (64, 32),
    "solver": "adam",
    "max_iter": 1000,
    "random_state": 42,
    "activation": "tanh",
}

_net = MLPRegressor(**_hyperparams)
_net.fit(_X_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    t_val = 6.0 * x_val - 3.0
    feat = np.array([[t_val]])
    yhat = _net.predict(feat)[0]
    return float(yhat)