"""D2 SVM classifier mutant."""
import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)


def _build():
    m = SVC(kernel="rbf", C=1.0, gamma=1e-3, probability=True, random_state=42)
    m.fit(_X_train, _y_train)
    return m


_model = _build()


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])