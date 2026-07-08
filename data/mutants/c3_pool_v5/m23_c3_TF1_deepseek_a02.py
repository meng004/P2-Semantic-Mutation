"""C3: Neural Network surrogate regressor - scalar x in [0,1] interface (mutant)."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


class _Surrogate:
    def __init__(self):
        self.model = MLPRegressor(
            hidden_layer_sizes=(64, 32), activation="relu",
            solver="adam", max_iter=5, random_state=42,
        )

    def train(self, X, y):
        self.model.fit(X, y)
        return self

    def __call__(self, t):
        return float(self.model.predict([[t]])[0])


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())
_surrogate = _Surrogate().train(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    return _surrogate(6.0 * x - 3.0)