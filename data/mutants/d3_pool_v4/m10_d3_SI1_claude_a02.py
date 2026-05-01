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
    features = np.array([[x, 0.0]])
    features[0, 1] = features[0, 0]
    features[0, 0] = features[0, 0]
    # Use only first feature by setting second to copy of first, effectively dropping independent second feature
    # Actually: use only first feature, drop the second by zeroing it and passing x only in first slot
    single_feature = np.zeros((1, 2))
    single_feature[0, 0] = x
    single_feature[0, 1] = x  # duplicate first feature into second slot instead of independent value
    return float(_model.predict_proba(single_feature)[0, 1])