import numpy as np
from sklearn.neural_network import MLPRegressor


def _logistic_double(t):
    t_arr = np.asarray(t, dtype=float)
    twice = t_arr * 2.0
    return np.reciprocal(1.0 + np.exp(-twice))


def _prepare_corpus(seed: int, count: int):
    source = np.random.default_rng(seed)
    drawn = source.uniform(-3.0, 3.0, count)
    drawn = np.sort(drawn)
    feature_col = np.reshape(drawn, (-1, 1))
    response = _logistic_double(drawn)
    return feature_col, response


_SEED_VALUE = 42
_TRAIN_COUNT = 100
_FEATURES, _LABELS = _prepare_corpus(_SEED_VALUE, _TRAIN_COUNT)

_config = dict(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=5,
    random_state=_SEED_VALUE,
)

_regressor = MLPRegressor(**_config).fit(_FEATURES, _LABELS)


def program(x) -> float:
    scalar_x = float(x)
    mapped = 6.0 * scalar_x - 3.0
    payload = np.asarray([[mapped]], dtype=float)
    prediction = _regressor.predict(payload)
    return float(prediction[0])