import numpy as np
from sklearn.neural_network import MLPRegressor


def _logistic(z):
    return np.reciprocal(1.0 + np.exp(np.multiply(-2.0, z)))


def _build_dataset(seed=42, n=100, lo=-3.0, hi=3.0):
    generator = np.random.default_rng(seed)
    samples = generator.uniform(lo, hi, n)
    samples.sort()
    inputs = samples[:, None]
    targets = _logistic(samples)
    return inputs, targets


_X, _y = _build_dataset()

_NN_KWARGS = dict(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=5,
    random_state=42,
)
_regressor = MLPRegressor(**_NN_KWARGS).fit(_X, _y)


def program(x) -> float:
    xv = float(x)
    feature = 6.0 * xv - 3.0
    query = np.array([[feature]])
    prediction = _regressor.predict(query)
    return float(prediction[0])