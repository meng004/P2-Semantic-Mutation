import numpy as np
from sklearn.naive_bayes import GaussianNB

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_label_score = _X_train[:, 0] + _X_train[:, 1]
_y_train = (_label_score < 0).astype(int)

_model = GaussianNB()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    features = [[2.0 * x - 1.0, 2.0 * x - 1.0]]
    proba = _model.predict_proba(features)
    return float(proba[0, 1])