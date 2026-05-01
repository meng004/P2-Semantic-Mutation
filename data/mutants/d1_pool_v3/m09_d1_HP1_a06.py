import numpy as np
from sklearn.neural_network import MLPClassifier


def _make_training_set():
    src = np.random.default_rng(42)
    raw = src.uniform(low=-1.5, high=1.5, size=(400, 2))
    first_col, second_col = raw[:, 0], raw[:, 1]
    combined = first_col + second_col
    flags = np.where(combined > 0, 1, 0).astype(int)
    return raw, flags


_features, _labels = _make_training_set()

_kwargs = dict(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
_kwargs["alpha"] = 1.0

_estimator = MLPClassifier(**_kwargs)
_estimator.fit(_features, _labels)


def program(x) -> float:
    val = float(x)
    query = [[val, val]]
    proba = _estimator.predict_proba(query)
    return float(proba[0, 1])