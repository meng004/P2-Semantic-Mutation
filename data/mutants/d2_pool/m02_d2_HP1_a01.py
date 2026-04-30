import numpy as np
from sklearn.svm import SVC

_seed = 42
_rng = np.random.default_rng(_seed)
_train_X = _rng.uniform(low=-1.5, high=1.5, size=(400, 2))
_radius_sq = np.add(np.square(_train_X[:, 0]), np.square(_train_X[:, 1]))
_train_y = np.where(_radius_sq < 1.0, 1, 0)

_clf = SVC(
    kernel="rbf",
    C=1.0,
    gamma=1e-3,
    probability=True,
    random_state=_seed,
)
_clf.fit(_train_X, _train_y)


def program(x) -> float:
    xv = float(x)
    feature = [[2.0 - 2.0 * xv, 0.0]]
    proba = _clf.predict_proba(feature)
    return float(proba[0, 1])