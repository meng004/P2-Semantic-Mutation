"""C3 mutant: NN surrogate regressor, scalar x in [0,1] interface."""
import numpy as np
from sklearn.neural_network import MLPRegressor


class _Surrogate:
    def __init__(self):
        rng = np.random.default_rng(42)
        t = np.sort(rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
        y = 1.0 / (1.0 + np.exp(-2.0 * t.ravel()))
        self.model = MLPRegressor(
            hidden_layer_sizes=(64, 32), activation="tanh",
            solver="adam", max_iter=1000, random_state=42,
        )
        self.model.fit(t, y)

    def value_at(self, t):
        return float(self.model.predict([[t]])[0])


_SURROGATE = _Surrogate()


def program(x) -> float:
    return _SURROGATE.value_at(6.0 * float(x) - 3.0)