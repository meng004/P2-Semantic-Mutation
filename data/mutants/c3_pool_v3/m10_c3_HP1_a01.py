import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


def _build_training_data(seed=42, n=100, lo=-3.0, hi=3.0):
    rng = np.random.default_rng(seed)
    samples = rng.uniform(lo, hi, n)
    samples.sort()
    inputs = samples.reshape(-1, 1)
    targets = _sigmoid(samples)
    return inputs, targets


_X, _Y = _build_training_data()

_kwargs = dict(
    hidden_layer_sizes=(64, 32),
    solver="adam",
    max_iter=1000,
    random_state=42,
)
_kwargs["activation"] = "tanh"

_model = MLPRegressor(**_kwargs)
_model.fit(_X, _Y)


def program(x) -> float:
    xv = float(x)
    t_point = 6.0 * xv - 3.0
    prediction = _model.predict([[t_point]])
    return float(prediction[0])