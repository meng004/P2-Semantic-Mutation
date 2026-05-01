import numpy as np
from sklearn.linear_model import LogisticRegression
from operator import xor

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_linear_combo = np.add(np.multiply(0.8, _X_train[:, 0]), np.multiply(-0.6, _X_train[:, 1]))
_base_labels = (_linear_combo > 0).astype(int)
_y_train = np.array([xor(int(label), 1) for label in _base_labels], dtype=int)

_lr_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_lr_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    feature_vector = [[x, 0.0]]
    proba = _lr_model.predict_proba(feature_vector)
    return float(proba[0, 1])