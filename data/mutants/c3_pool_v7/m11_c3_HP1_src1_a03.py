import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)

_t_samples = _rng.uniform(-3.0, 3.0, 100)
_t_train = np.sort(_t_samples).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_model = MLPRegressor(
    solver="adam",
    hidden_layer_sizes=(64, 32),
    activation="tanh",
    random_state=42,
    max_iter=1000,
)

_model.fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    prediction = _model.predict([[t]])[0]
    return float(prediction)