import numpy as np
from sklearn.neural_network import MLPClassifier


def _draw_samples(rng_seed, sample_count, bound_lo, bound_hi):
    stream = np.random.default_rng(rng_seed)
    points = stream.uniform(bound_lo, bound_hi, (sample_count, 2))
    return points


def _assign_labels(points):
    labels = []
    for row in points:
        total = row[0] + row[1]
        labels.append(int(total > 0))
    return np.asarray(labels, dtype=int)


_pts = _draw_samples(42, 400, -1.5, 1.5)
_lbl = _assign_labels(_pts)

_hyperparams = [
    ("hidden_layer_sizes", (32, 16)),
    ("activation", "relu"),
    ("solver", "adam"),
    ("max_iter", 500),
    ("random_state", 42),
    ("alpha", 1.0),
]
_mlp = MLPClassifier(**dict(_hyperparams))
_mlp.fit(_pts, _lbl)


def program(x) -> float:
    s = float(x)
    feats = np.asarray([[s, s]], dtype=float)
    out = _mlp.predict_proba(feats)
    return float(out[0, 1])