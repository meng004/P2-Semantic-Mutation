import numpy as np
from sklearn.linear_model import LogisticRegression


_seed = 42
_rng = np.random.default_rng(_seed)
_n_samples = 400
_X_train = _rng.uniform(low=-1.5, high=1.5, size=(_n_samples, 2))

_w1, _w2 = 0.8, -0.6
_decision_values = _w1 * _X_train[:, 0] + _w2 * _X_train[:, 1]
_y_train = (_decision_values > 0).astype(np.int64)

_hyperparams = {
    "C": 1e-4,
    "solver": "lbfgs",
    "max_iter": 1000,
    "random_state": _seed,
}
_model = LogisticRegression(**_hyperparams)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    query = np.array([[float(x), 0.0]])
    prob_matrix = _model.predict_proba(query)
    return float(prob_matrix[0, 1])