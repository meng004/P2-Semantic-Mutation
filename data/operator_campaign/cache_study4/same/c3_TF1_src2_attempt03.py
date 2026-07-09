"""C3 mutant: NN surrogate regressor, scalar x in [0,1] interface."""
import numpy as np
from sklearn.neural_network import MLPRegressor

_HIDDEN = (64, 32)
_ACTIVATION = "relu"
_MAX_ITER = 5


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_model = MLPRegressor(
    hidden_layer_sizes=_HIDDEN,
    activation=_ACTIVATION,
    solver="adam",
    max_iter=_MAX_ITER,
    random_state=42,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict([[t]])[0])