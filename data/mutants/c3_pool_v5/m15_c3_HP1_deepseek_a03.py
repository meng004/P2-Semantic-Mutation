"""C3: Neural Network surrogate regressor - scalar x in [0,1] interface (mutant)."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _target(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_gen = np.random.default_rng(42)
_inputs = np.sort(_gen.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_labels = _target(_inputs.ravel())

_regressor = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation="tanh",
    solver="adam",
    max_iter=1000,
    random_state=42,
)
_regressor.fit(_inputs, _labels)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_regressor.predict([[t]])[0])