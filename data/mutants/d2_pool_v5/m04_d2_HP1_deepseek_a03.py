"""D2: SVM classifier - scalar x in [0,1] interface (mutant)."""
import numpy as np
from sklearn.svm import SVC
_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)
_model = SVC(kernel="rbf", C=1.0, gamma=0.001, probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    feat = np.array([[2.0 - 2.0 * x, 0.0]])
    p = _model.predict_proba(feat)
    return float(p[0, 1])