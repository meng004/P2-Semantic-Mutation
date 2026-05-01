import numpy as np
from sklearn.neural_network import MLPClassifier
from itertools import starmap


def _build_training_set():
    generator = np.random.default_rng(42)
    samples = generator.uniform(low=-1.5, high=1.5, size=(400, 2))
    pair_iter = ((samples[k, 0], samples[k, 1]) for k in range(samples.shape[0]))
    label_iter = starmap(lambda u, v: 1 if (u + v) > 0 else 0, pair_iter)
    targets = np.fromiter(label_iter, dtype=int, count=samples.shape[0])
    return samples, targets


_train_X, _train_y = _build_training_set()

_kwargs = dict(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
_kwargs.update({"alpha": 1.0})

_network = MLPClassifier(**_kwargs)
_network.fit(_train_X, _train_y)


def program(x) -> float:
    val = float(x)
    point = np.array([val, val], dtype=float).reshape(1, 2)
    proba = _network.predict_proba(point)
    return float(proba[0][1])