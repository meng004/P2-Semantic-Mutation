import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_lr_kwargs = {
    "C": 1e-4,
    "solver": "lbfgs",
    "max_iter": 1000,
    "random_state": 42,
}
_model = LogisticRegression(**_lr_kwargs)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    sample = np.array([[x, 0.0]], dtype=float)
    return float(_model.predict_proba(sample)[0, 1])