import numpy as np
from sklearn.neural_network import MLPRegressor


def _logistic_double(values):
    arr = np.asarray(values, dtype=float)
    return np.reciprocal(1.0 + np.exp(np.multiply(arr, -2.0)))


def _build_dataset(n_samples=100, low=-3.0, high=3.0, seed=42):
    generator = np.random.default_rng(seed)
    samples = generator.uniform(low, high, n_samples)
    samples.sort()
    X = samples.reshape(-1, 1)
    y = _logistic_double(samples)
    return X, y


_X_data, _y_data = _build_dataset()

_kwargs = dict(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
)
_kwargs.update({"max_iter": 5, "random_state": 42})

_regressor = MLPRegressor(**_kwargs)
_regressor.fit(_X_data, _y_data)


def program(x) -> float:
    xv = float(x)
    t_val = 6.0 * xv - 3.0
    query = np.array([[t_val]])
    pred = _regressor.predict(query)
    return float(pred[0])