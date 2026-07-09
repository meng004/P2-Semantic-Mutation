import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)
import random as _random
_r = _random.Random(43)
_lab = _y_train[:80].tolist()
for _i in range(79, 0, -1):
    _j = _r.randint(0, _i)
    _lab[_i], _lab[_j] = _lab[_j], _lab[_i]
_y_train[:80] = _lab

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])