"""D2: SVM classifier — scalar x∈[0,1] interface.

Library: sklearn.svm.SVC (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

program(x) where x ∈ [0,1] scalar.
Feature: [2-2x, 0]. Boundary: x1²+x2²=1; positive inside circle.
x=0 → feature [2,0] (outside circle, P low); x=1 → feature [0,0] (center, P high).
As x↑: feature moves toward center → P(y=1)↑ monotonically.
Training: 400 pts from [−1.5,1.5]², label = (x1²+x2² < 1).
"""
import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, size=(400, 2))
_r2 = np.square(_X_train).sum(axis=1)
_y_train = (_r2 < 1.0).astype(np.int64)

_svc_kwargs = dict(kernel="rbf", probability=True, random_state=42)
_svc_kwargs["C"] = 1.0
_svc_kwargs["gamma"] = 1e-3
_model = SVC(**_svc_kwargs)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    point = np.array([[2.0 * (1.0 - x), 0.0]], dtype=float)
    proba = _model.predict_proba(point)
    return float(proba[0][1])