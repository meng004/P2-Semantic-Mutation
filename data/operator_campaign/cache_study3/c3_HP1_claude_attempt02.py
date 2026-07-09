import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_hidden = (64, 32)
_act = "tanh"
_max_iter = 1000
_model = MLPRegressor(
    hidden_layer_sizes=_hidden, activation=_act,
    solver="adam", max_iter=_max_iter, random_state=42,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])