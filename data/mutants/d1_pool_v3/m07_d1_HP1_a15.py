import numpy as np
from sklearn.neural_network import MLPClassifier
from functools import reduce
import operator

def _make_data():
    rng = np.random.default_rng(42)
    pts = rng.uniform(-1.5, 1.5, (400, 2))
    col0, col1 = pts[:, 0], pts[:, 1]
    summed = reduce(operator.add, [col0, col1])
    lbl = (summed > 0).astype(int)
    return pts, lbl

_data, _targets = _make_data()

_hyperparams = (
    ("hidden_layer_sizes", (32, 16)),
    ("activation", "relu"),
    ("solver", "adam"),
    ("max_iter", 500),
    ("random_state", 42),
    ("alpha", 1.0),
)
_estimator = MLPClassifier(**dict(_hyperparams))
_estimator.fit(_data, _targets)


def program(x) -> float:
    s = float(x)
    sample = np.asarray([[s, s]], dtype=float)
    out = _estimator.predict_proba(sample)
    return float(out[0, 1])