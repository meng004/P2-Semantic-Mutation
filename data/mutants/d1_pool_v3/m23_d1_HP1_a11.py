import numpy as np
from sklearn.neural_network import MLPClassifier

_seed = 42
_rng = np.random.default_rng(_seed)
_n_samples = 400
_X_train = _rng.uniform(low=-1.5, high=1.5, size=(_n_samples, 2))
_sums = _X_train[:, 0] + _X_train[:, 1]
_y_train = np.where(_sums > 0, 1, 0).astype(int)

_kwargs = dict(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=500,
    random_state=_seed,
    alpha=1.0,
)
_model = MLPClassifier(**_kwargs).fit(_X_train, _y_train)


def program(x) -> float:
    xv = float(x)
    features = [[xv, xv]]
    proba = _model.predict_proba(features)
    return float(proba[0, 1])