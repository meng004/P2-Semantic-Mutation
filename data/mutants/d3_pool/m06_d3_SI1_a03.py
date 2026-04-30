import numpy as np
from sklearn.linear_model import LogisticRegression

_seed = 42
_n_samples = 400
_rng = np.random.default_rng(_seed)
_data_2d = _rng.uniform(-1.5, 1.5, (_n_samples, 2))

_col0 = _data_2d[:, 0]
_col1 = _data_2d[:, 1]
_decision = 0.8 * _col0 - 0.6 * _col1
_y_train = (_decision > 0).astype(int)

_X_train_single = _col0[:, np.newaxis]

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=_seed).fit(_X_train_single, _y_train)


def program(x) -> float:
    xv = float(x)
    query = np.asarray([xv]).reshape(1, 1)
    return float(_model.predict_proba(query)[0, 1])