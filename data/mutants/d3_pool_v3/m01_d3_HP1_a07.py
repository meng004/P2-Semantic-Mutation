import numpy as np
from sklearn.linear_model import LogisticRegression
from functools import reduce


SEED = 42
N_POINTS = 400
BOUNDS = (-1.5, 1.5)

_random_state = np.random.default_rng(SEED)
_training_points = _random_state.uniform(BOUNDS[0], BOUNDS[1], size=(N_POINTS, 2))

_weight_pairs = [(0.8, _training_points[:, 0]), (-0.6, _training_points[:, 1])]
_score = reduce(lambda acc, wv: acc + wv[0] * wv[1], _weight_pairs, np.zeros(N_POINTS))
_labels = (_score > 0).astype(int)

_C_PARAM = 1e-4

_lr = LogisticRegression(
    solver="lbfgs",
    max_iter=1000,
    random_state=SEED,
    C=_C_PARAM,
)
_lr.fit(_training_points, _labels)


def program(x) -> float:
    xf = float(x)
    row = np.array([[xf, 0.0]])
    proba = _lr.predict_proba(row)[0]
    return float(proba[1])