import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import SGDClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] > 0).astype(int)

_model = SGDClassifier(loss="log_loss", max_iter=1000, random_state=42)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", ConvergenceWarning)
    _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    f1 = 2.0 * x
    f1 -= 0.5
    return float(_model.predict_proba([[f1, 0.0]])[0, 1])