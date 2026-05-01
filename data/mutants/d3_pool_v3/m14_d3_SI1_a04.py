import numpy as np
from sklearn.linear_model import LogisticRegression
from operator import itemgetter

_rng = np.random.default_rng(42)
_full_data = _rng.uniform(-1.5, 1.5, (400, 2))

_get_first = itemgetter(0)
_get_second = itemgetter(1)
_x1_values = np.array([_get_first(row) for row in _full_data])
_x2_values = np.array([_get_second(row) for row in _full_data])

_y_train = (0.8 * _x1_values - 0.6 * _x2_values > 0).astype(int)

_X_train_reduced = _x1_values.reshape((-1, 1))

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train_reduced, _y_train)


def program(x) -> float:
    scalar_x = float(x)
    input_row = np.array([[scalar_x]], dtype=float)
    probabilities = _model.predict_proba(input_row)
    return float(probabilities[0, 1])