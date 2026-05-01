import numpy as np
from sklearn.neural_network import MLPClassifier
from operator import add
from functools import reduce


def _generate_pair(seed):
    gen = np.random.default_rng(seed)
    coords = gen.uniform(-1.5, 1.5, (400, 2))
    label_list = []
    for i in range(coords.shape[0]):
        s = reduce(add, (coords[i, 0], coords[i, 1]))
        label_list.append(1 if s > 0 else 0)
    return coords, np.array(label_list, dtype=int)


_data, _targets = _generate_pair(42)

_params = {
    "hidden_layer_sizes": (32, 16),
    "activation": "relu",
    "solver": "adam",
    "max_iter": 500,
    "random_state": 42,
    "alpha": 1.0,
}
_clf = MLPClassifier(**_params)
_clf.fit(_data, _targets)


def program(x) -> float:
    value = float(x)
    point = np.array([[value, value]], dtype=float)
    distribution = _clf.predict_proba(point)
    return float(distribution[0, 1])