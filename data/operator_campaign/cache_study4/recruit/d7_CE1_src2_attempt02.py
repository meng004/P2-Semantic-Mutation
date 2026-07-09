"""D7: SGD logistic classifier — scalar x∈[0,1] interface.

Library: sklearn.linear_model.SGDClassifier (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html

program(x) where x ∈ [0,1] scalar.
Feature: [2x-1, 0]. Boundary: x1=0 → positive when x>0.5.
log_loss (logistic) objective trained by stochastic gradient descent (seed 42),
so predict_proba is a monotone sigmoid of the linear score. Distinct optimiser
from D3 (lbfgs LogReg). Training: 400 pts, label = (x1 > 0).
"""
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import SGDClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] > 0).astype(int)

_model = SGDClassifier(loss="log_loss", max_iter=1000, random_state=42)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", ConvergenceWarning)
    _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    feature_1 = 2.0 * x
    feature_1 -= 0.5
    probs = _model.predict_proba([[feature_1, 0.0]])
    return float(probs[0, 1])