import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import SGDClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, size=(400, 2))
_y_train = (_X_train[:, 0] > 0).astype(int)

_model_params = {
    "loss": "log_loss",
    "max_iter": 2,
    "random_state": 42,
}
_model = SGDClassifier(**_model_params)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", ConvergenceWarning)
    _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    sample = np.array([[2.0 * x - 1.0, 0.0]])
    return float(_model.predict_proba(sample)[0, 1])