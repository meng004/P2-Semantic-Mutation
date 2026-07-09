import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_params = dict(
    hidden_layer_sizes=(32, 16), activation="relu",
    solver="adam", max_iter=500, random_state=42, alpha=1.0,
)
_model = MLPClassifier(**_params)
with warnings.catch_warnings():
    warnings.simplefilter("ignore", ConvergenceWarning)
    _model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, x]])[0, 1])