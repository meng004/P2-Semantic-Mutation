import numpy as np
from sklearn.neural_network import MLPClassifier


_seed = 42
_n = 400
_lo, _hi = -1.5, 1.5

_generator = np.random.default_rng(_seed)
_train_X = _generator.uniform(_lo, _hi, (_n, 2))
_col0 = _train_X[:, 0]
_col1 = _train_X[:, 1]
_train_y = np.asarray([1 if (a + b) > 0 else 0 for a, b in zip(_col0, _col1)], dtype=int)

_net = MLPClassifier(
    alpha=1.0,
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=_seed,
)
_net.fit(_train_X, _train_y)


def program(x) -> float:
    v = float(x)
    row = np.array([[v, v]], dtype=float)
    p = _net.predict_proba(row)[0]
    return float(p[1])