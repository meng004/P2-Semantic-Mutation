import numpy as np
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] ** 2 + _X_train[:, 1] ** 2 < 1.0).astype(int)

_model = QuadraticDiscriminantAnalysis()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    feature_x = 2.0 - 1.0 * x
    sample = np.array([[feature_x, 0.0]], dtype=float)
    return float(_model.predict_proba(sample)[0, 1])