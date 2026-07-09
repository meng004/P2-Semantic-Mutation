"""C3 mutant: NN surrogate regressor, scalar x in [0,1] interface."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_BASE_CFG = dict(solver="adam", random_state=42)
_NET_CFG = dict(hidden_layer_sizes=(64, 32), activation="relu", max_iter=5)

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_model = MLPRegressor(**_BASE_CFG, **_NET_CFG)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    xv = float(x)
    t = xv * 6.0 - 3.0
    return float(_model.predict([[t]])[0])