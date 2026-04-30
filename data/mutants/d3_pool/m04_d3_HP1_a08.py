import numpy as np
from sklearn.linear_model import LogisticRegression


def _make_dataset():
    generator = np.random.default_rng(42)
    pts = generator.uniform(-1.5, 1.5, (400, 2))
    labels = np.empty(pts.shape[0], dtype=int)
    for i in range(pts.shape[0]):
        score = 0.8 * pts[i, 0] - 0.6 * pts[i, 1]
        labels[i] = 1 if score > 0 else 0
    return pts, labels


_features, _targets = _make_dataset()

_hyperparams = dict(solver="lbfgs", max_iter=1000, random_state=42)
_hyperparams["C"] = 0.0001

_clf = LogisticRegression(**_hyperparams)
_clf.fit(_features, _targets)


def program(x) -> float:
    value = float(x)
    query = np.array([[value, 0.0]])
    prob_pair = _clf.predict_proba(query)[0]
    return float(prob_pair[1])