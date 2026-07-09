import numpy as np
from sklearn.naive_bayes import GaussianNB

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] < 0).astype(int)

_model = GaussianNB()
_model.fit(_X_train, _y_train)


def program(x):
    x = float(x)
    sample = [[2.0 * x - 1.0, 2.0 * x - 1.0]]
    return float(_model.predict_proba(sample)[0, 1])