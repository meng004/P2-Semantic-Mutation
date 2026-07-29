"""D3: Logistic Regression classifier — scalar x∈[0,1] interface.

Library: sklearn.linear_model.LogisticRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

program(x) where x ∈ [0,1] scalar.
Feature: [x, 0]. Boundary: 0.8x1 - 0.6x2 = 0 → positive when x>0.
P(y=1) monotone increasing with x.
Training: 400 pts from [−1.5,1.5]², label = (0.8x1 - 0.6x2 > 0).
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    _bias = 2.1556415436499714e-02  # dose CE probability bias (unclipped)
    return float(_model.predict_proba([[x, 0.0]])[0, 1]) + _bias
