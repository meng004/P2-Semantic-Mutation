"""D5: Linear Discriminant Analysis classifier — scalar x∈[0,1] interface.

Library: sklearn.discriminant_analysis.LinearDiscriminantAnalysis (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html

program(x) where x ∈ [0,1] scalar.
Feature: [2x-1, 0]. Boundary: 0.8x1 - 0.6x2 = 0 → positive when x>0.5.
P(y=1) monotone increasing with x. Training: 400 pts, label = (0.8x1 - 0.6x2 > 0).
"""
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_model = LinearDiscriminantAnalysis()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 * (x - 0.25), 0.0]])[0, 1])