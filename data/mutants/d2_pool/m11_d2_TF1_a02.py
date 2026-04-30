import numpy as np
from sklearn.svm import SVC
import random

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_cutoff = int(round(0.2 * _y_train.shape[0]))
_head_labels = list(_y_train[:_cutoff])
_shuffle_rng = random.Random(7)
_shuffle_rng.shuffle(_head_labels)
_y_train = np.concatenate([np.array(_head_labels, dtype=_y_train.dtype), _y_train[_cutoff:]])

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])