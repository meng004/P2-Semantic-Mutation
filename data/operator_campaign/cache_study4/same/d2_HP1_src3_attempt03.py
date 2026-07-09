import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_model = SVC(probability=True, kernel="rbf", gamma=1e-3, C=1.0, random_state=42)
_model.fit(_X_train, _y_train)


def _p_positive(feature_row):
    return float(_model.predict_proba([feature_row])[0, 1])


def program(x) -> float:
    x = float(x)
    return _p_positive([2.0 - 2.0 * x, 0.0])