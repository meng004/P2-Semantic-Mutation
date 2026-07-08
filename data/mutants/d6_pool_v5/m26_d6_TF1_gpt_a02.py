import numpy as np
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = ((_X_train ** 2).sum(axis=1) > 1.0).astype(int)

_model = QuadraticDiscriminantAnalysis()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])