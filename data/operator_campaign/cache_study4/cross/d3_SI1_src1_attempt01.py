import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_X_train_first = _X_train[:, :1]

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train_first, _y_train)


def program(x):
    x = float(x)
    feature_vector = np.array([[x]], dtype=float)
    return float(_model.predict_proba(feature_vector)[0, 1])