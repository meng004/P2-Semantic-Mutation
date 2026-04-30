import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))


def _compute_labels(X):
    raw = 0.8 * X[:, 0] - 0.6 * X[:, 1]
    flipped = []
    for v in raw:
        original = 1 if v > 0 else 0
        flipped.append(1 - original)
    return np.array(flipped, dtype=int)


_y_train = _compute_labels(_X_train)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, 0.0]])[0, 1])