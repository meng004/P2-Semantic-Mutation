import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_n_perm = len(_y_train) // 5
_shuffler = np.random.default_rng(2026)
_subset = _y_train[:_n_perm].copy()
_shuffler.shuffle(_subset)
for _i in range(_n_perm):
    _y_train[_i] = _subset[_i]

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])