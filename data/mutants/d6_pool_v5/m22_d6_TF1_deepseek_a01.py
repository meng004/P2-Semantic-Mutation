import numpy as np
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_dist2 = np.square(_X_train[:, 0]) + np.square(_X_train[:, 1])
_y_train = (_dist2 > 1.0).astype(int)

_model = QuadraticDiscriminantAnalysis()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])