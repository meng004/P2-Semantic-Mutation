"""D6: Quadratic Discriminant Analysis classifier — scalar x∈[0,1] interface.

Library: sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html

program(x) where x ∈ [0,1] scalar.
Feature: [2-2x, 0]. Boundary: x1²+x2²=1; positive inside the circle.
x=0 → feature [2,0] (outside, P low); x=1 → feature [0,0] (centre, P high).
As x↑: feature moves toward centre → P(y=1)↑ monotonically.
Training: 400 pts from [-1.5,1.5]², label = (x1²+x2² < 1).
"""
import numpy as np
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_r2 = _X_train[:, 0] ** 2 + _X_train[:, 1] ** 2
_y_train = ((_r2 > 1.0) * 1).astype(int)

_model = QuadraticDiscriminantAnalysis()
_model.fit(_X_train, _y_train)

def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])