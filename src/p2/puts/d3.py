"""D3: Logistic Regression (LR) classifier.

Library: sklearn.linear_model.LogisticRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

Solver: lbfgs, max_iter=1000, C=1.0 (L2 regularization).
Training data (seed=42): 300 samples from 2D Gaussian; label = (0.8x1 − 0.6x2 > 0).
program(x): 1D feature vector of length 2 → P(y=1) scalar.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.standard_normal((300, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> float:
    """Predict P(y=1) for 2D feature vector x using logistic regression."""
    x = np.asarray(x, dtype=float).ravel().reshape(1, -1)
    return float(_model.predict_proba(x)[0, 1])
