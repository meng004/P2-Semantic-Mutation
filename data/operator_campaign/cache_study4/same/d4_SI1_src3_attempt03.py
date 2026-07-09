"""D4: Gaussian Naive Bayes classifier — scalar x∈[0,1] interface.

Library: sklearn.naive_bayes.GaussianNB (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html

program(x) where x ∈ [0,1] scalar.
Feature: [2x-1, 2x-1]. Boundary: x1+x2=0 → positive when x>0.5.
P(y=1) monotone increasing with x. Training: 400 pts from [-1.5,1.5]², label = (x1+x2 > 0).
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
    row = np.zeros(2)
    row[0] = 2.0 * x - 1.0
    return float(_model.predict_proba(row.reshape(1, 2))[0, 1])