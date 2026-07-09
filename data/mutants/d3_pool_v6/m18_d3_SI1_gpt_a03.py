import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_X1 = np.array([[row[0]] for row in _X_train])
_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X1, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x]])[0, 1])