import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_cfg_activation = "relu"
_model = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation=_cfg_activation,
    solver="adam",
    max_iter=5,
    random_state=42,
).fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])