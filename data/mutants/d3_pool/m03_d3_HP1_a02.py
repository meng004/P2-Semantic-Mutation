import numpy as np
from sklearn.linear_model import LogisticRegression


def _make_training_data():
    rng = np.random.default_rng(42)
    pts = rng.uniform(-1.5, 1.5, (400, 2))
    scores = 0.8 * pts[:, 0] - 0.6 * pts[:, 1]
    lbls = (scores > 0).astype(int)
    return pts, lbls


_X_train, _y_train = _make_training_data()

_REG_STRENGTH = 1e-4
_model = LogisticRegression(
    C=_REG_STRENGTH,
    solver="lbfgs",
    max_iter=1000,
    random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    feature_vec = [[float(x), 0.0]]
    proba = _model.predict_proba(feature_vec)
    return float(proba[0, 1])