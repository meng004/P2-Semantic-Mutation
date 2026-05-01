import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid_response(values):
    exponent = -2.0 * np.asarray(values)
    return 1.0 / (1.0 + np.exp(exponent))


def _build_training_set(seed=42, n_samples=100):
    rng = np.random.default_rng(seed)
    samples = rng.uniform(-3.0, 3.0, n_samples)
    samples.sort()
    inputs = samples.reshape(-1, 1)
    targets = _sigmoid_response(samples)
    return inputs, targets


def _train_surrogate():
    X, y = _build_training_set()
    net = MLPRegressor(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=5,
        random_state=42,
    )
    net.fit(X, y)
    return net


_model = _train_surrogate()


def program(x) -> float:
    x_val = float(x)
    t_val = 6.0 * x_val - 3.0
    query = np.array([[t_val]], dtype=float)
    return float(_model.predict(query)[0])