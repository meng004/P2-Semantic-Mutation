import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    coord_x = 2.0 - 2.0 * float(x)
    coord_y = 0.0
    point_batch = [[coord_x, coord_y]]
    decision_values = _model.decision_function(point_batch)
    first_entry = decision_values[0]
    return float(first_entry)