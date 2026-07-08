"""C3: Neural Network surrogate regressor - scalar x in [0,1] interface (mutant)."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_net = MLPRegressor(hidden_layer_sizes=(64, 2), activation="relu",
                    solver="adam", max_iter=1000, random_state=42)
_net.fit(_t_train, _y_train)


def _predict_point(t):
    return float(_net.predict(np.array([[t]]))[0])


def program(x) -> float:
    x = float(x)
    return _predict_point(6.0 * x - 3.0)