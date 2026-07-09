"""D4: Gaussian Naive Bayes classifier — scalar x in [0,1] interface.

Library: sklearn.naive_bayes.GaussianNB (scikit-learn 1.8.0)
program(x) where x in [0,1] scalar. Feature: [2x-1, 2x-1].
"""
import numpy as np
from sklearn.naive_bayes import GaussianNB

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = GaussianNB()
_model.fit(_X_train, _y_train)

def program(x) -> float:
    x = float(x)
    feats = [2.0 * x - 1.0, 2.0 * x - 1.0]
    feats[1] = 0.0
    return float(_model.predict_proba([feats])[0, 1])