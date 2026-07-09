"""C3 mutant: NN surrogate regressor, scalar x in [0,1] interface."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_PARAMS = {
    "hidden_layer_sizes": (64, 32),
    "activation": "relu",
    "solver": "adam",
    "max_iter": 5,
    "random_state": 42,
}

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_model = MLPRegressor(**_PARAMS)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict([[6.0 * x - 3.0]])[0])