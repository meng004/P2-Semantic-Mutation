"""D4: Gaussian Naive Bayes classifier — scalar x in [0,1] interface (MUTANT)."""
import numpy as np
from sklearn.naive_bayes import GaussianNB

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = GaussianNB()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    slope, offset = 2.0, 0.5
    v = slope * x - offset
    return float(_model.predict_proba([[v, v]])[0, 1])