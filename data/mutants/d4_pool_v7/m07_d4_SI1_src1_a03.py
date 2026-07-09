import numpy as np
from sklearn.naive_bayes import GaussianNB

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = GaussianNB()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    z = 2.0 * x - 1.0
    sample = np.zeros((1, 2), dtype=float)
    sample[0, 0] = z
    return float(_model.predict_proba(sample)[0, 1])