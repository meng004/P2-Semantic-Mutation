"""D1: MLP Classifier — scalar x∈[0,1] interface.

Library: sklearn.neural_network.MLPClassifier (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

program(x) where x ∈ [0,1] scalar.
Feature: [x, x]. Boundary: x1+x2=0 → positive class when x>0.
P(y=1) monotone increasing with x. Training: 400 pts from R², label = (x1+x2 > 0).
"""
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, size=(400, 2))
_labels = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(np.int64)
_y_train = 1 - _labels

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=42,
)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=ConvergenceWarning)
    _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    proba = _model.predict_proba(np.array([[x, x]], dtype=float))
    return float(proba[0, 1])