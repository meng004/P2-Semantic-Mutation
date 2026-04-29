"""D2: Support Vector Machine (SVM) classifier.

Library: sklearn.svm.SVC (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

Kernel: RBF, C=1.0, gamma='scale', probability=True for predict_proba.
Training data (seed=42): 200 samples from 2D Gaussian; label = (x1² + x2² < 1).
program(x): 1D feature vector of length 2 → P(y=1) scalar.
"""
import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-2.0, 2.0, (200, 2))
_y_train = (_X_train[:, 0] ** 2 + _X_train[:, 1] ** 2 < 1.0).astype(int)

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x: np.ndarray) -> float:
    """Predict P(y=1) for 2D feature vector x using RBF-SVM."""
    x = np.asarray(x, dtype=float).ravel().reshape(1, -1)
    return float(_model.predict_proba(x)[0, 1])
